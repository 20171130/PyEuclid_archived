import multiprocessing as mp
import time
import os
import json
from sympy import sympify
from tqdm import tqdm

from pyeuclid.formalization.state import State
from pyeuclid.formalization.relation import *
from pyeuclid.engine.inference_rule import inference_rule_sets
from pyeuclid.engine.deductive_database import DeductiveDatabase
from pyeuclid.engine.algebraic_system import AlgebraicSystem
from pyeuclid.engine.proof_generator import ProofGenerator
from pyeuclid.engine.engine import Engine
from stopit import ThreadingTimeout as Timeout

use_new = False
include_new = "new_" if use_new else ""
RESULTS_PATH = f"{include_new}results.jsonl"
TIMEOUT = 1200
NUM_WORKERS = 32
with open(RESULTS_PATH, "w") as f:
    pass  # This will truncate the file


def process_problem(idx, return_dict):
    try:
        if not os.path.isfile(f"data/Geometry3K/{idx}/problem.py"):
            return_dict["result"] = {"problem_number": idx, "status": "skip", "time": 0}
            return

        namespace = {}
        with open(f'data/Geometry3K/{idx}/problem.py', "r") as file:
            exec(file.read(), namespace)
        conditions = namespace.get("conditions")
        goal = namespace.get("goal")
        solution = namespace.get("solution")
        diagrammatic_relations = set(namespace.get(f"{include_new}diagrammatic_relations"))
        for i in conditions:
            if isinstance(i, Between):
                diagrammatic_relations.discard(NotCollinear(i.p1,i.p2,i.p3))

        state = State()
        state.silent = True
        state.load_problem(conditions=conditions, goal=goal)
        rs = []
        for r in list(diagrammatic_relations):
            f = True
            ps = r.get_points()
            for p in ps:
                if p not in list(state.points):
                    f = False
                    break
            if f:
                rs.append(r)
                    
        
        state.add_relations(rs)

        deductive_database = DeductiveDatabase(state, outer_theorems=inference_rule_sets['basic'] + inference_rule_sets['complex'])
        algebraic_system = AlgebraicSystem(state)
        proof_generator = ProofGenerator(state)
        engine = Engine(state, deductive_database, algebraic_system)

        t = time.time()
        
        with Timeout(600) as tt:
            engine.search()
        result = state.complete()
        if result is None:
            state.try_complex = True
            engine.deductive_database.closure = False
            with Timeout(600) as tt:
                engine.search()
            result = state.complete()
        
        t = time.time() - t

        if result is not None:
            correct = (result is True or abs((sympify(result).evalf() - sympify(solution).evalf()) / (sympify(solution).evalf() + 1e-4)) < 2e-2)
            status = "solved" if correct else "wrong"
        else:
            status = "unsolved"

        return_dict["result"] = {
            "problem_number": idx,
            "status": status,
            "time": str(t),
            "proposed": str(sympify(result)) if result is not None else '',
            "ground-truth": str(sympify(solution)) if solution is not None else ''
        }
    except Exception as e:
        return_dict["result"] = {"problem_number": idx, "status": "error", "error": str(e), "time": 0}

def run_with_timeout(idx, timeout):
    mgr = mp.Manager()
    return_dict = mgr.dict()
    p = mp.Process(target=process_problem, args=(idx, return_dict))
    p.start()
    p.join(timeout)
    if p.is_alive():
        p.terminate()
        p.join()
        return {"problem_number": idx, "status": "timeout", "time": 0}
    return return_dict.get("result", {"problem_number": idx, "status": "error", "error": "no result returned", "time": 0})

def append_result_to_file(result):
    with open(RESULTS_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(result) + "\n")

def worker_loop(task_queue, progress_queue):
    while True:
        try:
            idx = task_queue.get(timeout=2)
        except:
            break
        result = run_with_timeout(idx, timeout=TIMEOUT)
        append_result_to_file(result)
        progress_queue.put(1)

def main():
    indices = list(range(2401, 3002))

    mp.set_start_method("fork", force=True)  # or 'spawn' on Windows

    task_queue = mp.Queue()
    progress_queue = mp.Queue()

    for idx in indices:
        task_queue.put(idx)

    workers = []
    for _ in range(NUM_WORKERS):
        p = mp.Process(target=worker_loop, args=(task_queue, progress_queue))
        p.start()
        workers.append(p)

    with tqdm(total=len(indices)) as pbar:
        completed = 0
        while completed < len(indices):
            progress_queue.get()
            completed += 1
            pbar.update(1)

    for p in workers:
        p.join()

if __name__ == "__main__":
    main()
