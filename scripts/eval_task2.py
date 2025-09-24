#!/usr/bin/env python3
import argparse
import asyncio
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import aiohttp
import aiofiles
from tqdm.asyncio import tqdm
from openai import OpenAI  # sync client


# ---------- IO helpers ----------

def load_dataset(path: Path) -> List[Dict[str, Any]]:
    with path.open("r", encoding="utf-8") as f:
        head = f.read(1)
        f.seek(0)
        if head == "[":
            data = json.load(f)
            if not isinstance(data, list):
                raise ValueError("Top-level JSON must be a list.")
            return data
        else:
            return [json.loads(line) for line in f if line.strip()]

def ensure_parent_dir(p: Path):
    p.parent.mkdir(parents=True, exist_ok=True)

def to_abs_file_url(p: Union[str, Path]) -> str:
    return f"file://{Path(p).expanduser().resolve()}"

def parse_instruction(instr: str) -> Tuple[str, bool]:
    s = instr.lstrip()
    if s.startswith("<image>\n"):
        return s[len("<image>\n"):], True
    if s.startswith("<image>"):
        rest = s[len("<image>"):]
        return rest.lstrip("\n"), True
    return instr, False

def build_messages(instruction_text: str,
                   images: Optional[List[str]],
                   image_first: bool) -> List[Dict[str, Any]]:
    def image_parts(imgs: List[str]) -> List[Dict[str, Any]]:
        return [
            {"type": "image_url", "image_url": {"url": to_abs_file_url(p)}}
            for p in imgs
        ]
    imgs = images or []
    parts: List[Dict[str, Any]] = []
    if image_first and imgs:
        parts.extend(image_parts(imgs))
        parts.append({"type": "text", "text": instruction_text})
    else:
        parts.append({"type": "text", "text": instruction_text})
        if imgs:
            parts.extend(image_parts(imgs))
    return [{"role": "user", "content": parts}]


# ---------- Server discovery & readiness ----------

def read_hostfile(hostfile: Path) -> Optional[str]:
    if not hostfile.exists():
        return None
    txt = hostfile.read_text(encoding="utf-8").strip()
    if not txt or ":" not in txt:
        return None
    host, port = txt.split(":", 1)
    if not host.strip() or not port.strip():
        return None
    return f"http://{host.strip()}:{port.strip()}"

def resolve_server_url(args) -> str:
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

async def wait_for_ready(base_url: str, timeout_s: float, interval_s: float = 2.0):
    deadline = time.time() + timeout_s
    url = f"{base_url}/models"
    last_err = None
    async with aiohttp.ClientSession() as session:
        while time.time() < deadline:
            try:
                async with session.get(url, timeout=5) as resp:
                    if 200 <= resp.status < 300:
                        return
            except Exception as e:
                last_err = e
            await asyncio.sleep(interval_s)
    raise SystemExit(f"ERROR: vLLM server not ready at {url} within {timeout_s}s. Last error: {last_err!r}")


# ---------- Single-sample evaluator (async wrapper) ----------

async def evaluate_item_async(
    client: OpenAI,
    model: str,
    item: Dict[str, Any],
    temperature: float,
    top_p: float,
    max_tokens: int,
    print_fn=None,
) -> Dict[str, Any]:
    raw_instr = item.get("instruction", "") or ""
    images: List[str] = item.get("images", []) or []
    instruction_text, image_first = parse_instruction(raw_instr)
    messages = build_messages(instruction_text, images, image_first=image_first)

    start = time.perf_counter()
    try:
        # Run sync client in a worker thread
        resp = await asyncio.to_thread(
            client.chat.completions.create,
            model=model,
            messages=messages,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
        )
        elapsed = time.perf_counter() - start

        text = ""
        if resp and getattr(resp, "choices", None):
            ch0 = resp.choices[0]
            msg = getattr(ch0, "message", None)
            if msg is not None:
                text = msg.content or ""

        if print_fn:
            print_fn("=" * 40)
            leading = "<image>\n" if image_first and images else ""
            print_fn(f"Prompt:\n{leading}{instruction_text}\n")
            print_fn(f"Model Output:\n{text}\n")

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


# ---------- Orchestration (async loop) ----------

async def main_async(args):
    base_url = resolve_server_url(args)
    print(f"[evaluator] Using server: {base_url}")
    if args.wait_ready > 0:
        print(f"[evaluator] Waiting up to {args.wait_ready}s for server readiness...")
        await wait_for_ready(base_url, args.wait_ready)

    data = load_dataset(args.data)
    if args.max_samples is not None:
        data = data[: args.max_samples]

    client = OpenAI(base_url=base_url, api_key=os.getenv("OPENAI_API_KEY", "EMPTY"))

    ensure_parent_dir(args.out)
    async with aiofiles.open(args.out, "w", encoding="utf-8") as fout:
        print_fn = (lambda s: sys.stdout.write(s + "\n")) if args.print_prompts else None
        # schedule tasks
        tasks = []
        for idx, item in enumerate(data):
            tasks.append(evaluate_item_async(
                client=client,
                model=args.model,
                item=item,
                temperature=args.temperature,
                top_p=args.top_p,
                max_tokens=args.max_tokens,
                print_fn=print_fn,
            ))
        # run concurrently with progress bar
        for idx, coro in enumerate(tqdm.as_completed(tasks, total=len(tasks), desc="Evaluating", dynamic_ncols=True)):
            res = await coro
            out = {
                "index": data[idx].get("index", idx),
                "instruction": data[idx].get("instruction", ""),
                "input": data[idx].get("input", ""),
                "reference_output": data[idx].get("output", None),
                "images": data[idx].get("images", []),
                **res,
            }
            await fout.write(json.dumps(out, ensure_ascii=False) + "\n")
            await fout.flush()


# ---------- CLI ----------

def parse_args():
    ap = argparse.ArgumentParser(description="Asynchronous evaluator for vLLM with hostfile discovery.")
    ap.add_argument("--data", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--model", type=str, required=True)
    ap.add_argument("--server", type=str, default=None)
    ap.add_argument("--hostfile", type=str, default=".vllm/vllm_server_host.txt")
    ap.add_argument("--wait_ready", type=int, default=60)
    ap.add_argument("--max_samples", type=int, default=None)
    ap.add_argument("--print_prompts", action="store_true")
    ap.add_argument("--temperature", type=float, default=0.7)
    ap.add_argument("--top_p", type=float, default=1.0)
    ap.add_argument("--max_tokens", type=int, default=2048)
    return ap.parse_args()

def main():
    args = parse_args()
    try:
        asyncio.run(main_async(args))
    except KeyboardInterrupt:
        print("Interrupted.", file=sys.stderr)


if __name__ == "__main__":
    main()
