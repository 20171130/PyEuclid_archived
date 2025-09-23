#!/usr/bin/env python3
import os
import json
from pathlib import Path
import shutil
from typing import List, Tuple, Optional

import asyncio
import random
import time
import argparse
from dataclasses import dataclass

from tqdm import tqdm
from openai import AsyncAzureOpenAI

# ===== NEW: Gemini SDK (optional) =====
try:
    import google.generativeai as genai
    _HAS_GEMINI = True
except Exception:
    _HAS_GEMINI = False


# ---------------------- Prompt builders ----------------------
def create_problem_prompt(problem: str, goal: str) -> str:
    full_prompt = f"""
You are given a plane geometry problem:

Problem: {problem}. Find {goal}.

Task:
- Rewrite the problem in clear, concise, and fluent language, preserving the original meaning.
- If any angles are given in radians, convert them to degrees.
- Output ONLY the rewritten problem, with no explanations or extra text.
"""
    return full_prompt.strip()


def create_proof_prompt(problem: str, proof: str) -> str:
    full_prompt = f"""
You are given a plane geometry problem and its corresponding solution:

Problem:
{problem}

Solution:
{proof}

Task:
- Rewrite the solution in clear, concise, and fluent language, simplifying trivial or redundant steps.
- Step-wise formatting is optional. Use it only when it improves clarity; otherwise, presenting the solution as a continuous paragraph is acceptable.
- If any angles are given in radians, convert them to degrees.
- Output ONLY the rewritten solution, with the final answer inside \\boxed{{}} at the end.
- Do NOT include the problem statement, explanations, or extra text.
"""
    return full_prompt.strip()


def create_problem_prompt_choices(problem: str, goal: str, answer: str, n_choices: int = 4) -> str:
    # Build dynamic choice label list (A, B, C, ...)
    labels = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"[:max(2, n_choices)]
    labels_block = "\n".join(f"{ch}: ..." for ch in labels)

    full_prompt = f"""
You are given a plane geometry problem and its corresponding solution:

Problem: As shown in the figure, {problem}. {goal} = ( ).

Reference Answer (for correctness only):
{answer}

Task:
- Rewrite the problem in clear, concise, and fluent language, preserving the original meaning.
- Convert the task into a multiple-choice question with exactly {n_choices} options labeled {", ".join(labels)}.
- Use the reference solution ONLY to determine the correct numeric/choice answer.
- Create plausible distractors of comparable scale or magnitude to the correct answer.
- Ensure EXACTLY ONE option is correct.
- If any angles are given in radians, convert them to degrees.
- Output ONLY the rewritten problem followed by the choices, with no explanations or extra text.
- Do NOT include the solution, rationales, or extra text.

Output format:
<Rewritten problem statement>

Choices:
{labels_block}
"""
    return full_prompt.strip()


def create_proof_prompt_choices(problem: str, proof: str) -> str:
    full_prompt = f"""
You are given a plane geometry problem and its corresponding solution:

Problem:
{problem}

Solution:
{proof}

Task:
- Rewrite the solution in clear, concise, and fluent language, simplifying trivial or redundant steps.
- Step-wise formatting is optional. Use it only when it improves clarity; otherwise, presenting the solution as a continuous paragraph is acceptable.
- If any angles are given in radians, convert them to degrees.
- Ensure the final choice label matches the provided solution’s final answer.
- Output ONLY the rewritten solution, with the final CHOICE LABEL (e.g., A, B, C, or D) inside \\boxed{{}} at the end.
- Do NOT include the problem statement, explanations, or extra text.
"""
    return full_prompt.strip()


def build_problem_prompt(problem: str, goal: str, answer: Optional[str], mc_prob: float, n_choices: int = 4) -> Tuple[str, str]:
    """
    Decide the mode ('completion' or 'mc') and return (mode, prompt).
    - If proof is missing/empty, force 'completion'.
    - Otherwise sample using mc_prob (default 0.5).
    """
    has_answer = bool(answer and str(answer).strip())
    if has_answer and random.random() < mc_prob:
        return "mc", create_problem_prompt_choices(problem, goal, answer, n_choices=n_choices)
    return "completion", create_problem_prompt(problem, goal)


def build_proof_prompt(problem_for_proof: str, proof: str, mode: str) -> str:
    """
    Match the proof prompt to the chosen mode.
    """
    if mode == "mc":
        return create_proof_prompt_choices(problem_for_proof, proof)
    return create_proof_prompt(problem_for_proof, proof)


# ---------------------- Metrics ----------------------
@dataclass
class Prices:
    input_per_1k: float = 0.0  # USD per 1K tokens
    output_per_1k: float = 0.0


class Metrics:
    def __init__(self, prices: Prices):
        self.lock = asyncio.Lock()
        self.prices = prices
        self.n_calls = 0
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0
        self.total_latency_sec = 0.0
        self.total_cost_usd = 0.0

    async def record(self, prompt_tokens: int, completion_tokens: int, latency_sec: float):
        cost_in = (prompt_tokens / 1000.0) * self.prices.input_per_1k
        cost_out = (completion_tokens / 1000.0) * self.prices.output_per_1k
        async with self.lock:
            self.n_calls += 1
            self.total_prompt_tokens += prompt_tokens
            self.total_completion_tokens += completion_tokens
            self.total_latency_sec += latency_sec
            self.total_cost_usd += (cost_in + cost_out)

    def snapshot(self) -> dict:
        n = max(self.n_calls, 1)
        return {
            "calls": self.n_calls,
            "avg_latency_s": self.total_latency_sec / n,
            "avg_prompt_tokens": self.total_prompt_tokens / n,
            "avg_completion_tokens": self.total_completion_tokens / n,
            "avg_total_tokens": (self.total_prompt_tokens + self.total_completion_tokens) / n,
            "total_cost_usd": self.total_cost_usd,
            "avg_cost_usd": self.total_cost_usd / n,
        }


# ----------------- Async Azure LLM wrapper (TEXT-ONLY) -----------------
class AsyncSimpleAzureLLM:
    def __init__(
        self,
        client: AsyncAzureOpenAI,
        deployment: str,
        system_prompt: Optional[str] = None,
        retries: int = 5,
        base_backoff_sec: float = 1.5,
        jitter_sec: float = 0.25,
    ):
        self.client = client
        self.deployment = deployment
        self.system_prompt = system_prompt
        self.retries = retries
        self.base_backoff_sec = base_backoff_sec
        self.jitter_sec = jitter_sec

    async def generate(
        self,
        user_prompt: str,
        system_prompt: Optional[str] = None,
    ) -> tuple[str, int, int, float]:
        """Return (text, prompt_tokens, completion_tokens, latency_sec)."""
        messages = []
        sys = self._pick(system_prompt, self.system_prompt)
        if sys:
            messages.append({"role": "system", "content": sys})
        messages.append({"role": "user", "content": user_prompt})

        last_err = None
        for attempt in range(1, self.retries + 1):
            try:
                t0 = time.perf_counter()
                resp = await self.client.chat.completions.create(
                    model=self.deployment,
                    messages=messages,
                )
                t1 = time.perf_counter()
                text = resp.choices[0].message.content or ""
                pt = getattr(resp.usage, "prompt_tokens", 0)
                ct = getattr(resp.usage, "completion_tokens", 0)
                return text, pt, ct, (t1 - t0)
            except Exception as e:
                last_err = e
                if attempt == self.retries:
                    raise
                sleep_s = (self.base_backoff_sec ** attempt) + random.uniform(0, self.jitter_sec)
                await asyncio.sleep(sleep_s)
        raise RuntimeError(f"Azure chat completion failed: {last_err}")

    @staticmethod
    def _pick(x, default):
        return default if x is None else x


# ----------------- Async Gemini LLM wrapper (TEXT-ONLY) -----------------
class AsyncSimpleGeminiLLM:
    """
    Async wrapper around google-generativeai for TEXT-ONLY prompts.
    Requires GEMINI_API_KEY and a model name (e.g., gemini-2.5-flash).
    """
    def __init__(
        self,
        api_key: str,
        model_name: str = "gemini-2.5-flash",
        system_instruction: Optional[str] = None,
        retries: int = 5,
        base_backoff_sec: float = 1.5,
        jitter_sec: float = 0.25,
    ):
        if not _HAS_GEMINI:
            raise RuntimeError("google-generativeai is not installed. Run: pip install google-generativeai")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY not set.")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name, system_instruction=system_instruction)
        self.retries = retries
        self.base_backoff_sec = base_backoff_sec
        self.jitter_sec = jitter_sec

    async def generate(
        self,
        user_prompt: str,
        system_prompt: Optional[str] = None,  # ignored
    ) -> tuple[str, int, int, float]:
        last_err = None
        for attempt in range(1, self.retries + 1):
            try:
                t0 = time.perf_counter()
                resp = await self.model.generate_content_async(user_prompt)
                t1 = time.perf_counter()
                text = resp.text or ""
                pt = 0
                ct = 0
                try:
                    um = getattr(resp, "usage_metadata", None)
                    if um:
                        pt = int(getattr(um, "prompt_token_count", 0) or 0)
                        ct = int(getattr(um, "candidates_token_count", 0) or 0)
                except Exception:
                    pass
                return text, pt, ct, (t1 - t0)
            except Exception as e:
                last_err = e
                if attempt == self.retries:
                    raise
                sleep_s = (self.base_backoff_sec ** attempt) + random.uniform(0, self.jitter_sec)
                await asyncio.sleep(sleep_s)
        raise RuntimeError(f"Gemini generate_content failed: {last_err}")


# ---------- Pricing + metrics (defaults; override via env if you want) ----------
DEFAULT_AZURE_PRICES = Prices(
    input_per_1k=float(os.getenv("PRICE_IN_PER_1K", "0.0025")),
    output_per_1k=float(os.getenv("PRICE_OUT_PER_1K", "0.0100")),
)

DEFAULT_GEMINI_PRICES = Prices(
    input_per_1k=float(os.getenv("GEMINI_PRICE_IN_PER_1K", "0.0003")),
    output_per_1k=float(os.getenv("GEMINI_PRICE_OUT_PER_1K", "0.0025")),
)


# ---------- Concurrency ----------
MAX_CONCURRENCY = int(os.getenv("MAX_CONCURRENCY", "1000"))


# ---------- Discovery ----------
def collect_paths(root: str) -> Tuple[List[str], List[str]]:
    data_json_list, image_file_list = [], []
    for entry in tqdm(Path(root).rglob("*data.json")):
        sample_dir = entry.parent
        data_json_list.append(str(sample_dir / "data.json"))
        image_file_list.append(str(sample_dir / "diagram.jpg"))
    return sorted(data_json_list), sorted(image_file_list)


# ---------- One-sample processing ----------
async def process_one(
    idx: int,
    total: int,
    data_json: str,
    image_file: str,
    *,
    model,  # either AsyncSimpleAzureLLM or AsyncSimpleGeminiLLM
    sem: asyncio.Semaphore,
    dataset_dir: str,
    dst_dataset_dir: str,
    print_prompts: bool,
    print_outputs: bool,
    metrics: Metrics,
    mc_prob: float,
    n_choices: int,
) -> Optional[str]:
    """Process a single sample. NOTE: We DO NOT send images to the model; we only COPY them."""
    async with sem:
        logs = [("\n" + "=" * 80)]
        logs.append(f"[{idx+1}/{total}] File: {data_json}")
        logs.append("-" * 80)

        try:
            with open(data_json, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            logs.append(f"Failed to read/parse {data_json}: {e}")
            print("\n".join(logs))
            return data_json

        informal_problem = data.get("informal_problem", "")
        informal_goal = data.get("informal_goal", "")
        informal_proof = data.get("informal_proof", "")
        answer = data.get("solution", "")

        # 1) Build problem prompt based on mode (50/50 by default)
        mode, prompt_problem = build_problem_prompt(
            informal_problem, informal_goal, answer, mc_prob=mc_prob, n_choices=n_choices
        )
        if print_prompts:
            logs.append(f">>> PROBLEM PROMPT ({mode.upper()}) >>>")
            logs.append(prompt_problem)
            logs.append("-" * 80)

        try:
            refined_problem, pt1, ct1, lat1 = await model.generate(user_prompt=prompt_problem)
        except Exception as e:
            logs.append(f"Model error (problem): {e}")
            print("\n".join(logs))
            return data_json

        await metrics.record(pt1, ct1, lat1)

        if print_outputs:
            logs.append("<<< PROBLEM OUTPUT <<<")
            logs.append(refined_problem)
            logs.append("-" * 80)

        # 2) Proof prompt matched to the same mode
        prompt_proof = build_proof_prompt(refined_problem, informal_proof, mode=mode)
        if print_prompts:
            logs.append(f">>> PROOF PROMPT ({mode.upper()}) >>>")
            logs.append(prompt_proof)
            logs.append("-" * 80)

        try:
            refined_proof, pt2, ct2, lat2 = await model.generate(user_prompt=prompt_proof)
        except Exception as e:
            logs.append(f"Model error (proof): {e}")
            print("\n".join(logs))
            return data_json

        await metrics.record(pt2, ct2, lat2)

        if print_outputs:
            logs.append("<<< PROOF OUTPUT <<<")
            logs.append(refined_proof)
            logs.append("=" * 80 + "\n")

        # 3) Write outputs & COPY image file
        try:
            rel = Path(data_json).relative_to(Path(dataset_dir))
            dst_data_json = Path(dst_dataset_dir) / rel
            dst_image_file = Path(dst_dataset_dir) / Path(image_file).relative_to(Path(dataset_dir))

            dst_data_json.parent.mkdir(parents=True, exist_ok=True)
            data["mode"] = mode  # record which format was used
            data["refined_problem"] = refined_problem
            data["refined_proof"] = refined_proof
            with open(dst_data_json, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)

            if Path(image_file).exists():
                dst_image_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(image_file, dst_image_file)
        except Exception as e:
            logs.append(f"Output error: {e}")
            print("\n".join(logs))
            return data_json

        # Always print the header + errors; only print bodies if flags are set
        print("\n".join(logs))
        return None


# ---------------------- Main ----------------------
async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--provider",
        type=str,
        choices=["azure", "gemini"],
        default=os.getenv("LLM_PROVIDER", "azure"),
        help="LLM provider to use (azure or gemini).",
    )
    parser.add_argument(
        "--dataset-dir",
        type=str,
        default="task1/calculation_922_new_template",
        help="Root directory containing source samples (default: task1/calculation_919_samples_template)",
    )
    parser.add_argument(
        "--dst-dataset-dir",
        type=str,
        default="task1/calculation_922_new_llm", help="Destination directory to write refined samples (default: task1/calculation_919_llm)",
    )
    parser.add_argument("--start-idx", type=int, default=0, help="Start index (inclusive)")
    parser.add_argument("--end-idx", type=int, default=None, help="End index (exclusive)")
    parser.add_argument("--print-prompts", action="store_true", help="Print LLM prompts")
    parser.add_argument("--print-outputs", action="store_true", help="Print LLM outputs")

    # NEW: control flip & reproducibility
    parser.add_argument("--mc-prob", type=float, default=0.9, help="Probability of multiple-choice mode (default 0.5)")
    parser.add_argument("--n-choices", type=int, default=4, help="Number of choices when in MC mode (default 4)")
    parser.add_argument("--seed", type=int, default=0, help="Random seed for reproducibility")

    args = parser.parse_args()

    if args.seed is not None:
        random.seed(args.seed)

    dataset_dir = args.dataset_dir
    dst_dataset_dir = args.dst_dataset_dir

    data_json_list, image_file_list = collect_paths(dataset_dir)
    total_all = len(data_json_list)

    start = max(args.start_idx, 0)
    end = total_all if args.end_idx is None else min(args.end_idx, total_all)
    data_json_list = data_json_list[start:end]
    image_file_list = image_file_list[start:end]

    total = len(data_json_list)
    print(f"Found {total_all} samples in total. Processing range [{start}, {end}) → {total} samples.")
    print(f"dataset_dir: {dataset_dir}")
    print(f"dst_dataset_dir: {dst_dataset_dir}")
    print(f"provider: {args.provider}")
    print(f"mc_prob: {args.mc_prob}, n_choices: {args.n_choices}, seed: {args.seed}")

    # --------- Build provider + pricing + metrics ----------
    if args.provider == "azure":
        client = AsyncAzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        )
        AZURE_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")
        model = AsyncSimpleAzureLLM(
            client=client,
            deployment=AZURE_DEPLOYMENT,
            system_prompt=os.getenv("AZURE_SYSTEM_PROMPT") or None,
        )
        prices = DEFAULT_AZURE_PRICES
        closer = client.close
    else:
        if not _HAS_GEMINI:
            raise RuntimeError("google-generativeai is not installed. Run: pip install google-generativeai")
        GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        model = AsyncSimpleGeminiLLM(
            api_key=os.getenv("GEMINI_API_KEY", ""),
            model_name=GEMINI_MODEL,
            system_instruction=os.getenv("GEMINI_SYSTEM_PROMPT") or None,
        )
        prices = DEFAULT_GEMINI_PRICES

        async def closer():
            return

    metrics = Metrics(prices)

    if total == 0:
        await closer()
        return

    # Pricing banner
    print(f"Pricing (USD/1K tokens): input={prices.input_per_1k}, output={prices.output_per_1k}")

    sem = asyncio.Semaphore(int(os.getenv("MAX_CONCURRENCY", MAX_CONCURRENCY)))
    tasks = [
        process_one(
            i + start,
            total_all,
            dj,
            im,
            model=model,
            sem=sem,
            dataset_dir=dataset_dir,
            dst_dataset_dir=dst_dataset_dir,
            print_prompts=args.print_prompts,
            print_outputs=args.print_outputs,
            metrics=metrics,
            mc_prob=args.mc_prob,
            n_choices=args.n_choices,
        )
        for i, (dj, im) in enumerate(zip(data_json_list, image_file_list))
    ]

    error_list: List[str] = []
    for coro in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc="Processing", unit="sample"):
        err = await coro
        if err:
            error_list.append(err)

    # Summary metrics
    snap = metrics.snapshot()
    print("\n=== METRICS SUMMARY ===")
    for k, v in snap.items():
        print(f"{k}: {v}")

    if error_list:
        print("\nThe following files had issues:")
        for p in error_list:
            print(" -", p)
    else:
        print("\nAll samples processed successfully.")

    await closer()


if __name__ == "__main__":
    asyncio.run(main())
