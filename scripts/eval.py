import os
import time
import json
import copy
import traceback
import argparse
from pathlib import Path

import requests
from stopit import ThreadingTimeout as TT
from concurrent.futures import ThreadPoolExecutor, as_completed

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


def ensure_dir(p):
    p.mkdir(parents=True, exist_ok=True)


def write_json(path, payload):
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


def chat_completions(
    base_url,
    model,
    messages,
    n,
    temperature,
    top_p,
    request_timeout=120.0,
):
    url = base_url.rstrip("/") + "/v1/chat/completions"
    headers = {"Authorization": "Bearer EMPTY"}
    payload = {
        "model": model,
        "messages": messages,
        "n": n,
        "temperature": temperature,
        "top_p": top_p,
    }
    r = requests.post(url, headers=headers, json=payload, timeout=request_timeout)
    r.raise_for_status()
    data = r.json()
    return [c["message"]["content"] for c in data.get("choices", [])]


def evaluate_candidate_on_cpu(
    raw_text,
    base_state,
    constructions_list,
    result_dir,
    engine_timeout_s,
    proof_timeout_s,
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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", type=str, default="http://127.0.0.1:8000")
    parser.add_argument("--model", type=str, default="saves/qwen2_5-math-7b/")
    parser.add_argument("--total-beams", type=int, default=32)
    parser.add_argument("--n-per-call", type=int, default=32)
    parser.add_argument("--cpu-workers", type=int, default=32)
    parser.add_argument("--max-tokens", type=float, default=1024)
    parser.add_argument("--temperature", type=float, default=1)
    parser.add_argument("--top-p", type=float, default=0.95)
    parser.add_argument("--engine-timeout", type=int, default=1200)
    parser.add_argument("--proof-timeout", type=int, default=1200)
    parser.add_argument("--problem-idx", type=int, default=None)
    args = parser.parse_args()
    utils.MAX_DIAGRAM_ATTEMPTS = MAX_DIAGRAM_ATTEMPTS

    task_id, task_count = get_array_info()
    print(
        f"[Array index-shard] task {task_id}/{task_count} base-url={args.base_url} model={args.model} "
        f"beams={args.total_beams} n_per_call={args.n_per_call} cpu_workers={args.cpu_workers}"
    )

    texts = parse_texts_from_file(str(DATA_TXT))
    if args.problem_idx:
        texts = [texts[args.problem_idx]]
    tot = 0
    solved_cnt = 0

    for idx, text in enumerate(texts):
        if not is_my_index(idx, task_id, task_count):
            continue
        if args.problem_idx:
            problem_id = args.problem_idx
        else:
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
                    samples = chat_completions(
                        base_url=args.base_url,
                        model=args.model,
                        messages=base_messages,
                        n=req_n,
                        temperature=args.temperature,
                        top_p=args.top_p,
                        request_timeout=120.0,
                    )
                except Exception as e:
                    print(f"[{problem_id}] LLM request failed at beams {total_done}-{total_done+req_n-1}: {e}")
                    break
                # for raw_text in samples:
                #     print('predicted', raw_text)
                #     result = evaluate_candidate_on_cpu(raw_text, state, constructions_list, result_dir, args.engine_timeout, args.proof_timeout)
                #     if result:
                #         print('solved')
                #         break
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
