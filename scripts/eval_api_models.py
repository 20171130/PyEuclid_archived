#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Unified runner for JGEX-AG-231 with LLM-assisted auxiliary constructions.
Backends: Gemini (google.generativeai) and OpenAI (chat.completions).
"""

import os
import time
import json
import copy
import traceback
import argparse
from pathlib import Path
from typing import Optional, Union, List

from stopit import ThreadingTimeout as TT
from concurrent.futures import ThreadPoolExecutor, as_completed

# ---- Your project imports ----
import pyeuclid.formalization.utils as utils
from pyeuclid.formalization.state import State
from pyeuclid.formalization.translation import (
    parse_texts_from_file,
    parse_construction_program,
)
from pyeuclid.formalization.construction_rule import *
from pyeuclid.formalization.relation import *
from pyeuclid.engine.deductive_database import DeductiveDatabase
from pyeuclid.engine.algebraic_system import AlgebraicSystem
from pyeuclid.engine.proof_generator import ProofGenerator
from pyeuclid.engine.engine import Engine

# ---- External LLM SDKs (install as needed) ----
# OpenAI SDK (>=1.0 style)
from openai import OpenAI
# Google Gemini SDK
import google.generativeai as genai
import google.api_core.exceptions


# =======================
# Provider wrappers
# =======================

class OpenAIProvider:
    """Minimal wrapper around OpenAI Chat Completions."""
    def __init__(self, api_key: str, model: str = "gpt-4o"):
        if not api_key:
            raise RuntimeError("OpenAI API key is required.")
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def generate_many(
        self,
        system_prompt: str,
        user_prompt: str,
        n: int,
        temperature: float,
        top_p: float,
        max_tokens: int,
        per_request_cap: int = 16,
    ) -> List[str]:
        """Return up to n texts using OpenAI n-per-call batching."""
        outs: List[str] = []
        remaining = int(n)
        while remaining > 0:
            take = min(per_request_cap, remaining)
            try:
                resp = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt.strip()},
                        {"role": "user", "content": user_prompt.strip()},
                    ],
                    temperature=float(temperature),
                    top_p=float(top_p),
                    max_tokens=int(max_tokens),
                    n=int(take),
                )
                for c in resp.choices:
                    txt = (c.message.content or "").strip()
                    if txt:
                        outs.append(txt)
            except Exception as e:
                print(f"An error occurred during OpenAI API call: {e}")
                break # Stop trying if an API error occurs
            remaining -= take
        return outs[:n]


class GeminiProvider:
    """Robust wrapper for the Google Gemini API."""
    def __init__(self, api_key: str, model: str = "gemini-2.5-pro"):
        if not api_key:
            raise RuntimeError("Gemini API key is required.")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name=model)

    def _single_call(
        self,
        prompt: str,
        candidate_count: int,
        temperature: float,
        top_p: float,
        max_tokens: int,
    ) -> List[str]:
        """Makes a single, robust call to the Gemini API."""
        gen_cfg = {
            "temperature": float(temperature),
            "top_p": float(top_p),
            "max_output_tokens": int(max_tokens),
            "candidate_count": int(candidate_count),
        }
        
        try:
            # The prompt is passed directly, not in a list.
            response = self.model.generate_content(prompt, generation_config=gen_cfg)

            # **Crucial Check**: Explicitly check for content blocking or safety issues.
            if not response.candidates:
                feedback = getattr(response, 'prompt_feedback', 'No feedback available.')
                print(
                    f"Gemini API Warning: No candidates returned. Possible safety block. Feedback: {feedback}",
                )
                return []

            outs = []
            for candidate in response.candidates:
                # Simplified and canonical text extraction.
                if candidate.content and candidate.content.parts:
                    text = "".join(part.text for part in candidate.content.parts).strip()
                    if text:
                        outs.append(text)
            return outs

        except google.api_core.exceptions.GoogleAPICallError as e:
            print(f"Gemini API Call Error: {e}")
            return []
        except Exception as e:
            # Catch other unexpected errors during the API call.
            print(f"An unexpected error occurred during Gemini API call: {e}")
            traceback.print_exc()
            return []

    def generate_many(
        self,
        prompt: str,
        n: int,
        temperature: float,
        top_p: float,
        max_tokens: int,
        per_request_cap: int = 8,
    ) -> List[str]:
        """Return up to n texts using candidate_count per request."""
        outs: List[str] = []
        remaining = int(n)
        while remaining > 0:
            take = min(per_request_cap, remaining)
            # Exception handling is now inside _single_call.
            generated_texts = self._single_call(
                prompt=prompt,
                candidate_count=take,
                temperature=temperature,
                top_p=top_p,
                max_tokens=max_tokens,
            )
            
            # If the API call fails or returns nothing, stop trying.
            if not generated_texts:
                print("Gemini API call returned no content. Halting further requests for this problem.")
                break
            
            outs.extend(generated_texts)
            # Decrement by the number of samples we actually received.
            remaining -= len(generated_texts)
        
        return outs[:n]


# =======================
# Unified LLM dispatcher
# =======================

def chat_completions_unified(
    provider_name: str,
    provider_obj,
    messages: List[dict],
    n: int,
    temperature: float,
    top_p: float,
    max_tokens: int,
) -> List[str]:
    """
    A unified dispatcher that formats the prompt and calls the appropriate provider.
    
    Args:
        messages: A list of dicts, e.g., [{"role": "system", "content": ...}, {"role": "user", "content": ...}]
    
    Returns:
        A list of up to n generated strings.
    """
    sys_txt, user_txt = "", ""
    for m in messages:
        role = m.get("role")
        if role == "system":
            sys_txt += (m.get("content", "") or "") + "\n\n"
        elif role == "user":
            user_txt += (m.get("content", "") or "") + "\n"

    # Prompt formatting is now done ONCE here for efficiency and clarity.
    system_prompt = sys_txt.strip()
    user_prompt = user_txt.strip()
    final_prompt_for_gemini = (system_prompt + "\n\n" + user_prompt).strip()

    if provider_name == "gemini":
        # We now pass the single formatted prompt directly.
        return provider_obj.generate_many(
            prompt=final_prompt_for_gemini,
            n=n,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
            per_request_cap=8,
        )

    if provider_name == "openai":
        # OpenAI's API prefers separate system and user messages.
        return provider_obj.generate_many(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            n=n,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
            per_request_cap=16,
        )

    raise ValueError(f"Unknown provider: {provider_name}")


# =======================
# Task logic
# =======================

SYSTEM_PROMPT = (
    "You are an expert in plane geometry, specializing in identifying the most effective "
    "auxiliary constructions for solving geometry problems. Given a formal geometry problem, "
    "output only the essential auxiliary constructions required for the solution. "
    "Use existing points as inputs and give unique names to all newly constructed points. "
    "Each new point must be defined using no more than two auxiliary constructions."
)

DATA_TXT = Path("data/JGEX-AG-231.txt")
RESULTS_DIR = Path("results/JGEX-AG-231")
MAX_DIAGRAM_ATTEMPTS = None


def get_array_info():
    tid = int(os.environ.get("SLURM_ARRAY_TASK_ID", "0"))
    tcount = int(os.environ.get("SLURM_ARRAY_TASK_COUNT", "1"))
    return tid, tcount


def is_my_index(idx, task_id, task_count):
    return (idx % task_count) == task_id


def ensure_dir(p: Path):
    p.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, payload):
    path.write_text(json.dumps(payload, indent=4), encoding="utf-8")


def build_problem_json(constructions_list, state):
    constructions = [c for group in constructions_list for c in group]
    problem_str = ", ".join(str(c) for c in constructions)
    goal_str = str(state.goal)
    return {"problem": problem_str, "goal": goal_str}


def solve_with_engine(state, timeout_s):
    dd = DeductiveDatabase(state)
    alg = AlgebraicSystem(state)
    eng = Engine(state, dd, alg)
    t0 = time.time()
    with TT(timeout_s):
        eng.run()
    return (state.complete() is not None, time.time() - t0)


def generate_proof_str(state, timeout_s):
    pg = ProofGenerator(state)
    pg.max_equation_length_perstep = None
    with TT(timeout_s):
        pg.run()
        proof = pg.get_proof()
        if proof is None:
            return None
        return pg.get_proof_str()


def group_aux_by_outputs(aux):
    grouped = []
    for construction in aux:
        if not grouped:
            grouped.append([construction])
        else:
            last = grouped[-1]
            if len(last[-1].outputs) == len(construction.outputs) and all(
                o1 == o2 for o1, o2 in zip(last[-1].outputs, construction.outputs)
            ):
                last.append(construction)
            else:
                grouped.append([construction])
    return grouped


def evaluate_candidate_on_cpu(
    raw_text: str,
    base_state: State,
    constructions_list,
    result_dir: Path,
    engine_timeout_s: int,
    proof_timeout_s: int,
):
    try:
        aux = parse_construction_program(raw_text)
    except Exception:
        return None
    aux_grouped = group_aux_by_outputs(aux)

    st = State()
    st.silent = True
    st.goal = base_state.goal
    st.diagram = copy.deepcopy(base_state.diagram)

    try:
        for group in aux_grouped:
            st.diagram.add_constructions(group)
    except Exception:
        return None
    try:
        for group in constructions_list + aux_grouped:
            st.add_constructions(group)
    except Exception:
        return None

    solved, _ = solve_with_engine(st, engine_timeout_s)
    if not solved:
        return None

    try:
        proof_str = generate_proof_str(st, proof_timeout_s)
        if not proof_str:
            return None
        return proof_str, aux
    except Exception:
        return None


def format_proof_with_aux(aux, proof_str):
    aux_line = ", ".join(str(a) for a in aux)
    header = "Auxiliary construction" if len(aux) == 1 else "Auxiliary constructions"
    return f"{header} (from LLM):\n{aux_line}\n{proof_str}"


# =======================
# Main
# =======================

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--provider", choices=["gemini", "openai"], required=True)

    # Gemini
    parser.add_argument("--gemini-model", type=str, default="gemini-2.5-pro")
    parser.add_argument("--gemini-api-key", type=str, default=os.environ.get("GEMINI_API_KEY", ""))

    # OpenAI
    parser.add_argument("--openai-model", type=str, default="gpt-4o")
    parser.add_argument("--openai-api-key", type=str, default=os.environ.get("OPENAI_API_KEY", ""))

    # Common sampling / batching
    parser.add_argument("--total-beams", type=int, default=32)
    parser.add_argument("--n-per-call", type=int, default=32)
    parser.add_argument("--cpu-workers", type=int, default=32)
    parser.add_argument("--max-tokens", type=int, default=1024)
    parser.add_argument("--temperature", type=float, default=1.0)
    parser.add_argument("--top-p", type=float, default=0.95)

    # Timeouts and selection
    parser.add_argument("--engine-timeout", type=int, default=1200)
    parser.add_argument("--proof-timeout", type=int, default=1200)

    args = parser.parse_args()
    utils.MAX_DIAGRAM_ATTEMPTS = MAX_DIAGRAM_ATTEMPTS

    # Init provider
    if args.provider == "gemini":
        provider = GeminiProvider(api_key=args.gemini_api_key, model=args.gemini_model)
        model_info = args.gemini_model
    else:
        provider = OpenAIProvider(api_key=args.openai_api_key, model=args.openai_model)
        model_info = args.openai_model

    task_id, task_count = get_array_info()
    print(
        f"[Array index-shard] task {task_id}/{task_count} "
        f"provider={args.provider} model={model_info} beams={args.total_beams} "
        f"n_per_call={args.n_per_call} cpu_workers={args.cpu_workers}"
    )

    texts = parse_texts_from_file(str(DATA_TXT))

    tot = 0
    solved_cnt = 0

    for idx, text in enumerate(texts):
        if not is_my_index(idx, task_id, task_count):
            continue

        problem_id = idx + 1
        result_dir = RESULTS_DIR / f"{problem_id}"
        ensure_dir(result_dir)
        proof_path = result_dir / "proof.txt"
        if proof_path.exists():
            continue

        state = State()
        state.silent = True

        try:
            diagram_path = result_dir / "diagram.jpg"
            constructions_list = state.load_problem_from_text(str(text), str(diagram_path))

            data_json = result_dir / "data.json"
            if not data_json.exists():
                write_json(data_json, build_problem_json(constructions_list, state))

            print(f"[{problem_id}] Processing (task {task_id}) | {text}")
            tot += 1

            # Try engine first
            solved, elapsed = solve_with_engine(state, args.engine_timeout)
            if solved:
                print(f"[{problem_id}] Solved by engine in {elapsed:.2f}s; generating proof...")
                proof_str = generate_proof_str(state, args.proof_timeout)
                if proof_str:
                    proof_path.write_text(proof_str, encoding="utf-8")
                    print(f"[{problem_id}] Proof generated and saved.")
                    solved_cnt += 1
                    continue
                else:
                    print(f"[{problem_id}] Proof generation failed/timeout after engine solve; continuing to LLM beams.")

            # LLM phase
            data = json.loads((result_dir / "data.json").read_text())
            base_messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Problem: {data['problem']}\nGoal: {data['goal']}\n"},
            ]

            total_done = 0
            success = False
            while total_done < args.total_beams and not success:
                remaining = args.total_beams - total_done
                req_n = min(args.n_per_call, remaining)
                try:
                    samples = chat_completions_unified(
                        provider_name=args.provider,
                        provider_obj=provider,
                        messages=base_messages,
                        n=req_n,
                        temperature=args.temperature,
                        top_p=args.top_p,
                        max_tokens=args.max_tokens,
                    )
                except Exception as e:
                    print(f"[{problem_id}] LLM request failed at beams {total_done}-{total_done+req_n-1}: {e}")
                    break

                with ThreadPoolExecutor(max_workers=args.cpu_workers) as ex:
                    futures = [
                        ex.submit(
                            evaluate_candidate_on_cpu,
                            raw_text,
                            state,
                            constructions_list,
                            result_dir,
                            args.engine_timeout,
                            args.proof_timeout,
                        )
                        for raw_text in samples
                    ]
                    for fut in as_completed(futures):
                        try:
                            result = fut.result()
                            if result:
                                proof_str, aux = result
                                for f in futures:
                                    f.cancel()
                                payload = format_proof_with_aux(aux, proof_str)
                                proof_path.write_text(payload, encoding="utf-8")
                                print(f"[{problem_id}] Solved via LLM beam; proof saved.")
                                success = True
                                break
                        except Exception:
                            # ignore failures from a single candidate
                            pass

                total_done += req_n

            if success:
                solved_cnt += 1
            else:
                print(f"[{problem_id}] Not solved after {args.total_beams} beams")

        except KeyboardInterrupt:
            raise
        except BaseException as e:
            print(f"[{problem_id}] ERROR")
            print(e)
            print(traceback.format_exc())

    if tot > 0:
        print(f"[Array {task_id}] Solved {solved_cnt}/{tot} = {solved_cnt / tot:.2%}")
    else:
        print(f"[Array {task_id}] No assigned cases.")


if __name__ == "__main__":
    main()
