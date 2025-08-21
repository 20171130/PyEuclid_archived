import os
import time
import json
import copy
import shutil
import traceback
import argparse
from pathlib import Path
from typing import Optional, Tuple, List

import requests
from stopit import ThreadingTimeout as TT
from concurrent.futures import ThreadPoolExecutor, as_completed

# pyeuclid imports
import pyeuclid.formalization.utils as utils
from pyeuclid.formalization.state import State
from pyeuclid.formalization.translation import (
    parse_texts_from_file,
    parse_construction_program,
)
from pyeuclid.engine.deductive_database import DeductiveDatabase
from pyeuclid.engine.algebraic_system import AlgebraicSystem
from pyeuclid.engine.proof_generator import ProofGenerator
from pyeuclid.engine.engine import Engine


# --------------------------
# Defaults / Config
# --------------------------

SYSTEM_PROMPT = (
    "You are an expert in plane geometry, specializing in identifying the most effective "
    "auxiliary constructions for solving geometry problems. Given a formal geometry problem, "
    "output only the essential auxiliary constructions required for the solution. "
    "Use existing points as inputs and give unique names to all newly constructed points. "
    "Each new point must be defined using no more than two auxiliary constructions."
)

DATA_TXT = Path("data/JGEX-AG-231.txt")
DIAGRAMS_DIR = Path("diagrams/JGEX-AG-231")
RESULTS_DIR = Path("results/JGEX-AG-231")

MAX_DIAGRAM_ATTEMPTS = 1000


# --------------------------
# Helpers
# --------------------------

def get_array_info() -> Tuple[int, int]:
    """Return (task_id, task_count) from Slurm env; defaults to (0, 1)."""
    tid = int(os.environ.get("SLURM_ARRAY_TASK_ID", "0"))
    tcount = int(os.environ.get("SLURM_ARRAY_TASK_COUNT", "1"))
    return tid, tcount


def is_my_index(idx: int, task_id: int, task_count: int) -> bool:
    return (idx % task_count) == task_id


def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=4), encoding="utf-8")


def build_problem_json(constructions_list, state: State) -> dict:
    # Only the ORIGINAL problem constructions (no LLM aux saved)
    constructions = [c for group in constructions_list for c in group]
    problem_str = ", ".join(str(c) for c in constructions)
    goal_str = str(state.goal)
    return {"problem": problem_str, "goal": goal_str}


def solve_with_engine(state: State, timeout_s: int) -> Tuple[bool, float]:
    dd = DeductiveDatabase(state)
    alg = AlgebraicSystem(state)
    eng = Engine(state, dd, alg)

    t0 = time.time()
    with TT(timeout_s):
        eng.run()
    return (state.complete() is not None, time.time() - t0)


def generate_proof_str(state: State, timeout_s: int) -> Optional[str]:
    """Run ProofGenerator with a timeout; return proof string or None."""
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


def openai_chat_completions(
    base_url: str,
    model: str,
    messages: List[dict],
    n: int,
    max_tokens: int,
    temperature: float,
    top_p: float,
    request_timeout: float = 120.0,
) -> List[str]:
    """
    Minimal OpenAI-compatible call to a vLLM server.
    """
    url = base_url.rstrip("/") + "/v1/chat/completions"
    headers = {"Authorization": "Bearer EMPTY"}  # vLLM generally ignores auth by default
    payload = {
        "model": model,
        "messages": messages,
        "n": n,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "top_p": top_p,
    }
    r = requests.post(url, headers=headers, json=payload, timeout=request_timeout)
    r.raise_for_status()
    data = r.json()
    return [c["message"]["content"] for c in data.get("choices", [])]


# --------------------------
# Beam evaluation (CPU-parallel)
# --------------------------

def evaluate_candidate_on_cpu(
    raw_text: str,
    base_state: State,
    constructions_list,
    result_dir: Path,
    engine_timeout_s: int,
    proof_timeout_s: int,
) -> Optional[str]:
    """
    Evaluate a single candidate (LLM beam) on CPU:
      - parse construction program
      - apply to a deepcopy of base_state
      - run engine with timeout
      - if solved, generate proof and return the proof string
    Returns proof_str if solved (and proof generated), else None.
    """
    try:
        aux = parse_construction_program(raw_text)
    except Exception:
        return None

    aux_grouped = group_aux_by_outputs(aux)

    st = copy.deepcopy(base_state)
    st.diagram.save_path = str(result_dir / "diagram.jpg")

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

    # Generate proof if solved
    try:
        proof_str = generate_proof_str(st, proof_timeout_s)
        return proof_str
    except Exception:
        return None


# --------------------------
# Main driver
# --------------------------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", type=str, default=os.environ.get("VLLM_BASE_URL", "http://127.0.0.1:8000"))
    parser.add_argument("--model", type=str, default=os.environ.get("VLLM_MODEL", "saves/qwen2_5-math-7b/full/sft"))
    parser.add_argument("--total-beams", type=int, default=int(os.environ.get("TOTAL_BEAMS", 512)))
    parser.add_argument("--n-per-call", type=int, default=int(os.environ.get("N_PER_CALL", 32)))
    parser.add_argument("--cpu-workers", type=int, default=int(os.environ.get("CPU_WORKERS", 32)))
    parser.add_argument("--max-tokens", type=int, default=int(os.environ.get("MAX_TOKENS", 256)))
    parser.add_argument("--temperature", type=float, default=float(os.environ.get("TEMPERATURE", 0.8)))
    parser.add_argument("--top-p", type=float, default=float(os.environ.get("TOP_P", 0.95)))
    parser.add_argument("--engine-timeout", type=int, default=int(os.environ.get("NUM_ENGINE_TIMEOUT", 1200)))
    parser.add_argument("--proof-timeout", type=int, default=int(os.environ.get("NUM_PROOF_TIMEOUT", 1200)))
    args = parser.parse_args()
    utils.MAX_DIAGRAM_ATTEMPTS = MAX_DIAGRAM_ATTEMPTS

    task_id, task_count = get_array_info()
    print(
        f"[Array index-shard] task {task_id}/{task_count} base-url={args.base_url} model={args.model} "
        f"beams={args.total_beams} n_per_call={args.n_per_call} cpu_workers={args.cpu_workers}"
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
        # If previously solved (proof exists), skip
        if proof_path.exists():
            continue

        state = State()
        state.silent = True

        try:
            diagram_path = DIAGRAMS_DIR / f"{problem_id}.jpg"
            constructions_list = state.load_problem_from_text(str(text), str(diagram_path))

            data_json = result_dir / "data.json"
            if not data_json.exists():
                # Only the original problem — NO LLM aux saved
                write_json(data_json, build_problem_json(constructions_list, state))

            dst = result_dir / "diagram.jpg"
            if not dst.exists():
                try:
                    shutil.copy(str(diagram_path), str(dst))
                except Exception:
                    pass

            print(f"[{problem_id}] Processing (task {task_id}) | {text}")
            tot += 1

            # Try engine-only first
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

            # Not solved by engine — do beam search with CPU-parallel evaluation
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
                    samples = openai_chat_completions(
                        base_url=args.base_url,
                        model=args.model,
                        messages=base_messages,
                        n=req_n,
                        max_tokens=args.max_tokens,
                        temperature=args.temperature,
                        top_p=args.top_p,
                        request_timeout=180.0,
                    )
                except Exception as e:
                    print(f"[{problem_id}] LLM request failed at beams {total_done}-{total_done+req_n-1}: {e}")
                    break

                # for raw_text in samples:
                #     proof_str = evaluate_candidate_on_cpu(raw_text, state, constructions_list,result_dir,args.engine_timeout,args.proof_timeout)
                #     if proof_str:
                #         print(proof_str)
                #         print(f"[{problem_id}] Solved via LLM beam; proof saved.")
                #         break

                # Evaluate beams concurrently on CPU threads; return proof_str when solved
                with ThreadPoolExecutor(max_workers=args.cpu_workers) as ex:
                    futures = [
                        ex.submit(
                            evaluate_candidate_on_cpu,
                            raw_text,
                            state,                  # deepcopied inside worker
                            constructions_list,
                            result_dir,
                            args.engine_timeout,
                            args.proof_timeout,
                        )
                        for raw_text in samples
                    ]
                    for fut in as_completed(futures):
                        try:
                            proof_str = fut.result()
                            if proof_str:
                                proof_path.write_text(proof_str, encoding="utf-8")
                                print(f"[{problem_id}] Solved via LLM beam; proof saved.")
                                success = True
                                # Cancel outstanding futures
                                for f in futures:
                                    f.cancel()
                                break
                        except Exception:
                            # ignore single-beam errors, continue
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
