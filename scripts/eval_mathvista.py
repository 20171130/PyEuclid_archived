#!/usr/bin/env python3
import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

import asyncio
from tqdm import tqdm
from openai import AsyncOpenAI  # async client

# If you want TRUE async file writes, pip install aiofiles
try:
    import aiofiles  # type: ignore
    _HAS_AIOFILES = True
except Exception:
    _HAS_AIOFILES = False

# ---------- IO helpers ----------

def load_dataset(path: Path) -> List[Dict[str, Any]]:
    with path.open("r") as f:
        data = json.load(f)
    return data.values()

def ensure_parent_dir(p: Path):
    p.parent.mkdir(parents=True, exist_ok=True)

def to_abs_file_url(p: Union[str, Path]) -> str:
    return f"file://{Path(p).expanduser().resolve()}"

def parse_instruction(instr: str) -> Tuple[str, bool]:
    """
    Return (text_without_marker, image_first_flag).
    If instruction starts with '<image>' (optionally followed by newline),
    we strip that marker and signal that image should be placed BEFORE the text.
    """
    s = instr.lstrip()  # tolerate accidental leading spaces
    if s.startswith("<image>\n"):
        return s[len("<image>\n"):], True
    if s.startswith("<image>"):
        # handle no-newline case, then strip any immediate newline spaces
        rest = s[len("<image>"):]
        return rest.lstrip("\n"), True
    return instr, False

def build_messages(instruction_text: str,
                   image: Optional[str],
                   image_first: bool) -> List[Dict[str, Any]]:
    """
    Build OpenAI-compatible multimodal chat message parts for a SINGLE image string.
    - If image_first is True, put the image BEFORE the text.
    - Otherwise, put text first then the image.
    """
    def one_image_part(img: str) -> Dict[str, Any]:
        return {"type": "image_url", "image_url": {"url": to_abs_file_url(img)}}

    parts: List[Dict[str, Any]] = []

    if image_first and image:
        parts.append(one_image_part(image))
        parts.append({"type": "text", "text": instruction_text})
    else:
        parts.append({"type": "text", "text": instruction_text})
        if image:
            parts.append(one_image_part(image))

    return [{"role": "user", "content": parts}]

# ---------- Server discovery & readiness ----------

def read_hostfile(hostfile: Path) -> Optional[str]:
    if not hostfile.exists():
        return None
    txt = hostfile.read_text(encoding="utf-8").strip()
    if not txt or ":" not in txt:
        return None
    host, port = txt.split(":", 1)
    host, port = host.strip(), port.strip()
    if not host or not port:
        return None
    return f"http://{host}:{port}"

def resolve_server_url(args) -> str:
    """Return a base_url that ALWAYS ends with /v1."""
    base_url: Optional[str] = None
    if args.server:
        base_url = args.server.strip()
    elif os.getenv("VLLM_BASE_URL", "").strip():
        base_url = os.getenv("VLLM_BASE_URL").strip()
    else:
        hf_url = read_hostfile(Path(args.hostfile))
        if hf_url:
            base_url = hf_url.strip()

    if not base_url:
        raise SystemExit(
            f"ERROR: Could not resolve server URL. Provide --server, "
            f"set VLLM_BASE_URL, or ensure a valid hostfile at {args.hostfile}."
        )

    base_url = base_url.rstrip("/")
    if not base_url.endswith("/v1"):
        base_url += "/v1"
    return base_url

def wait_for_ready(base_url: str, timeout_s: float, interval_s: float = 2.0):
    """Poll <base_url>/models (base_url already ends with /v1) until 2xx or timeout."""
    deadline = time.time() + timeout_s
    url = f"{base_url}/models"
    last_err = None
    while time.time() < deadline:
        try:
            req = Request(url, headers={"Accept": "application/json"})
            with urlopen(req, timeout=5) as resp:
                if 200 <= resp.status < 300:
                    return
        except (URLError, HTTPError, TimeoutError) as e:
            last_err = e
        time.sleep(interval_s)
    raise SystemExit(f"ERROR: vLLM server not ready at {url} within {timeout_s}s. Last error: {last_err!r}")

# ---------- Async evaluator ----------

async def evaluate_item_async(
    client: AsyncOpenAI,
    model: str,
    item: Dict[str, Any],
    temperature: float,
    top_p: float,
    max_tokens: int,
    print_prompts: bool = False,
) -> Dict[str, Any]:
    # Expected item fields:
    # { "index": int, "question": "<image>\n{problem}", "input": "", "output": "...(ignored)...",
    #   "resolved_image": "path/to/image.png" }  # SINGLE image string
    raw_instr = item.get("question", "") or ""
    image: Optional[str] = item.get("resolved_image", None)

    # Decide placement based on marker; override to True if you always want image first
    instruction_text, image_first = parse_instruction(raw_instr)
    image_first = True  # force image before text if desired

    # Build messages for single-image input
    messages = build_messages(instruction_text, image=image, image_first=image_first)

    start = time.perf_counter()
    try:
        resp = await client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
        )
        elapsed = time.perf_counter() - start

        # Extract assistant text safely
        text = ""
        if resp and getattr(resp, "choices", None):
            msg = resp.choices[0].message
            text = msg.content or ""

        if print_prompts:
            print("=" * 40)
            leading = "<image>\n" if image_first and image else ""
            print(f"Prompt:\n{leading}{instruction_text}\n")
            print(f"Model Output:\n{text}\n")

        usage = getattr(resp, "usage", None)
        usage_dict = {
            "prompt_tokens": getattr(usage, "prompt_tokens", None) if usage else None,
            "completion_tokens": getattr(usage, "completion_tokens", None) if usage else None,
            "total_tokens": getattr(usage, "total_tokens", None) if usage else None,
        }

        return {
            "ok": True,
            "elapsed_s": elapsed,
            "response_text": text,
            "usage": usage_dict,
        }
    except Exception as e:
        return {
            "ok": False,
            "elapsed_s": time.perf_counter() - start,
            "error": repr(e),
            "response_text": "",
            "usage": None,
        }

# ---------- Async orchestration with concurrency cap ----------

async def _eval_one_with_sem(
    sem: asyncio.Semaphore,
    client: AsyncOpenAI,
    model: str,
    item: Dict[str, Any],
    temperature: float,
    top_p: float,
    max_tokens: int,
    print_prompts: bool,
    idx: int,
):
    async with sem:
        res = await evaluate_item_async(
            client=client,
            model=model,
            item=item,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
            print_prompts=print_prompts,
        )
    return idx, item, res

async def main_async(args):
    base_url = resolve_server_url(args)
    print(f"[evaluator] Using server: {base_url}")
    if args.wait_ready > 0:
        print(f"[evaluator] Waiting up to {args.wait_ready}s for server readiness...")
        wait_for_ready(base_url, args.wait_ready)

    data = load_dataset(args.data)
    if args.max_samples is not None:
        data = data[: args.max_samples]

    # For vLLM OpenAI-compatible server, an API key can be any non-empty string
    client = AsyncOpenAI(base_url=base_url, api_key=os.getenv("OPENAI_API_KEY", "EMPTY"))
    ensure_parent_dir(args.out)

    # Build tasks with a concurrency limit
    sem = asyncio.Semaphore(args.concurrency)
    tasks = [
        asyncio.create_task(
            _eval_one_with_sem(
                sem, client, args.model, item,
                args.temperature, args.top_p, args.max_tokens,
                args.print_prompts, idx
            )
        )
        for idx, item in enumerate(data)
    ]

    # Collect all OUT dicts first (for sorting by their "index" field later)
    results_out: List[Dict[str, Any]] = []

    with tqdm(total=len(tasks), desc="Evaluating", dynamic_ncols=True) as pbar:
        for coro in asyncio.as_completed(tasks):
            idx, item, res = await coro
            out = {
                "index": item.get("pid", idx),         # preserve dataset's index if present
                "instruction": item.get("resolved_question", ""),
                "input": item.get("input", ""),
                "image": item.get("resolved_image", None),
                **res,
            }
            results_out.append(out)
            pbar.update(1)

    # 🔑 Sort strictly by the "index" field in the out dict
    results_out.sort(key=lambda o: o["index"])

    # Optional: detect duplicates and warn (does not stop execution)
    dup_check = {}
    dups = []
    for o in results_out:
        k = o["index"]
        dup_check[k] = dup_check.get(k, 0) + 1
        if dup_check[k] == 2:
            dups.append(k)
    if dups:
        print(f"[warning] Duplicate index values encountered (kept order after sort): {sorted(set(dups))}", file=sys.stderr)

    # Write sorted results
    if _HAS_AIOFILES:
        async with aiofiles.open(args.out, "w", encoding="utf-8") as fout:
            for out in results_out:
                await fout.write(json.dumps(out, ensure_ascii=False) + "\n")
                await fout.flush()
    else:
        with args.out.open("w", encoding="utf-8") as fout:
            for out in results_out:
                fout.write(json.dumps(out, ensure_ascii=False) + "\n")
                fout.flush()

# ---------- CLI ----------

def parse_args():
    ap = argparse.ArgumentParser(description="Asynchronous evaluator for vLLM with hostfile discovery.")
    ap.add_argument("--data", type=Path, required=True, help="Dataset (JSON array or JSONL).")
    ap.add_argument("--out", type=Path, required=True, help="Output JSONL path.")
    ap.add_argument("--model", type=str, required=True, help="Model id as shown by /v1/models.")
    # server discovery
    ap.add_argument("--server", type=str, default=None, help="Override base URL, e.g. http://host:port or http://host:port/v1")
    ap.add_argument("--hostfile", type=str, default=".vllm/vllm_server_host.txt", help="Hostfile path with 'HOST:PORT'")
    ap.add_argument("--wait_ready", type=int, default=60, help="Seconds to wait for /v1/models (0 to skip)")
    # runtime
    ap.add_argument("--max_samples", type=int, default=None, help="Evaluate at most this many samples from the dataset head")
    ap.add_argument("--print_prompts", action="store_true", help="Print prompt + model output")
    ap.add_argument("--concurrency", type=int, default=8, help="Max concurrent requests to the server")
    # generation params
    ap.add_argument("--temperature", type=float, default=0.7, help="Sampling temperature")
    ap.add_argument("--top_p", type=float, default=1.0, help="Nucleus sampling probability")
    ap.add_argument("--max_tokens", type=int, default=2048, help="Maximum new tokens to generate")
    return ap.parse_args()

def main():
    args = parse_args()
    try:
        asyncio.run(main_async(args))
    except KeyboardInterrupt:
        print("Interrupted.", file=sys.stderr)

if __name__ == "__main__":
    main()
