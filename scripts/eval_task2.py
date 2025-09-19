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

from tqdm import tqdm
from openai import OpenAI  # sync client

# ---------- IO helpers ----------

def load_dataset(path: Path) -> List[Dict[str, Any]]:
    with path.open("r", encoding="utf-8") as f:
        head = f.read(1)
        f.seek(0)
        if head == "[":  # JSON array
            data = json.load(f)
            if not isinstance(data, list):
                raise ValueError("Top-level JSON must be a list.")
            return data
        else:            # JSONL
            return [json.loads(line) for line in f if line.strip()]

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
                   images: Optional[List[str]],
                   image_first: bool) -> List[Dict[str, Any]]:
    """
    Build OpenAI-compatible multimodal chat message parts.
    - If image_first is True, put the image part(s) BEFORE the text.
    - Otherwise, put text first then image part(s).
    - Supports multiple images if provided (they'll all be included).
    """
    parts: List[Dict[str, Any]] = []

    def image_parts(imgs: List[str]) -> List[Dict[str, Any]]:
        return [
            {"type": "image_url", "image_url": {"url": to_abs_file_url(p)}}
            for p in imgs
        ]

    imgs = images or []
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

# ---------- Single-sample evaluator (sync) ----------

def evaluate_item_sync(
    client: OpenAI,
    model: str,
    item: Dict[str, Any],
    temperature: float,
    top_p: float,
    max_tokens: int,
    print_fn=None,
) -> Dict[str, Any]:
    # Your dataset format:
    # { "index": int, "instruction": "<image>\n{problem}", "input": "", "output": "...(ignored)...", "images": ["path"] }
    raw_instr = item.get("instruction", "") or ""
    images: List[str] = item.get("images", []) or []

    # Detect whether the instruction leads with <image>
    instruction_text, image_first = parse_instruction(raw_instr)

    # Build messages so the image is placed BEFORE the text if image_first is True
    messages = build_messages(instruction_text, images, image_first=image_first)

    start = time.perf_counter()
    try:
        resp = client.chat.completions.create(
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
            ch0 = resp.choices[0]
            msg = getattr(ch0, "message", None)
            if msg is not None:
                text = msg.content or ""

        if print_fn:
            print_fn("=" * 40)
            # Reconstruct a readable prompt preview:
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

# ---------- Orchestration (sync loop) ----------

def main_sync(args):
    base_url = resolve_server_url(args)
    print(f"[evaluator] Using server: {base_url}")
    if args.wait_ready > 0:
        print(f"[evaluator] Waiting up to {args.wait_ready}s for server readiness...")
        wait_for_ready(base_url, args.wait_ready)

    data = load_dataset(args.data)
    if args.max_samples is not None:
        data = data[: args.max_samples]

    # For vLLM OpenAI-compatible server, an API key can be any non-empty string
    client = OpenAI(base_url=base_url, api_key=os.getenv("OPENAI_API_KEY", "EMPTY"))

    ensure_parent_dir(args.out)
    with args.out.open("w", encoding="utf-8") as fout, tqdm(total=len(data), desc="Evaluating", dynamic_ncols=True) as pbar:
        print_fn = (lambda s: pbar.write(s)) if args.print_prompts else None

        for idx, item in enumerate(data):
            res = evaluate_item_sync(
                client=client,
                model=args.model,
                item=item,
                temperature=args.temperature,
                top_p=args.top_p,
                max_tokens=args.max_tokens,
                print_fn=print_fn,
            )
            out = {
                "index": item.get("index", idx),  # preserve index if present
                "instruction": item.get("instruction", ""),
                "input": item.get("input", ""),
                "reference_output": item.get("output", None),  # ignored for prompting, kept for logging
                "images": item.get("images", []),
                **res,
            }
            fout.write(json.dumps(out, ensure_ascii=False) + "\n")
            fout.flush()
            pbar.update(1)

# ---------- CLI ----------

def parse_args():
    ap = argparse.ArgumentParser(description="Synchronous evaluator for vLLM with hostfile discovery.")
    ap.add_argument("--data", type=Path, required=True, help="Dataset (JSON array or JSONL).")
    ap.add_argument("--out", type=Path, required=True, help="Output JSONL path.")
    ap.add_argument("--model", type=str, required=True, help="Model id as shown by /v1/models.")
    # server discovery
    ap.add_argument("--server", type=str, default=None, help="Override base URL, e.g. http://host:port or http://host:port/v1")
    ap.add_argument("--hostfile", type=str, default=".vllm/vllm_server_host.txt", help="Hostfile path with 'HOST:PORT'")
    ap.add_argument("--wait_ready", type=int, default=60, help="Seconds to wait for /v1/models (0 to skip)")
    # runtime
    ap.add_argument("--max_samples", type=int, default=None, help="Evaluate at most this many samples from the dataset head")
    ap.add_argument("--print_prompts", action="store_true", help="Print prompt + model output using tqdm-safe writes")
    # generation params
    ap.add_argument("--temperature", type=float, default=0.7, help="Sampling temperature")
    ap.add_argument("--top_p", type=float, default=1.0, help="Nucleus sampling probability")
    ap.add_argument("--max_tokens", type=int, default=2048, help="Maximum new tokens to generate")
    return ap.parse_args()

def main():
    args = parse_args()
    try:
        main_sync(args)
    except KeyboardInterrupt:
        print("Interrupted.", file=sys.stderr)

if __name__ == "__main__":
    main()
