import unittest
import time
import multiprocessing
from sympy import sympify
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor, as_completed, TimeoutError

from pyeuclid.formalization.state import State
from pyeuclid.formalization.relation import *
from pyeuclid.engine.inference_rule import inference_rule_sets
from pyeuclid.engine.deductive_database import DeductiveDatabase
from pyeuclid.engine.algebraic_system import AlgebraicSystem
from pyeuclid.engine.proof_generator import ProofGenerator
from pyeuclid.engine.engine import Engine

def run_single_problem(idx):
    try:
        namespace = {}
        with open(f'data/Geometry3K/{idx}/problem.py', "r") as file:
            exec(file.read(), namespace)
        conditions = namespace.get("conditions")
        goal = namespace.get("goal")
        solution = namespace.get("solution")
        diagrammatic_relations = namespace.get("diagrammatic_relations")

        state = State()
        state.try_complex = True
        state.silent = True
        state.load_problem(conditions=conditions, goal=goal)
        state.add_relations(diagrammatic_relations)

        deductive_database = DeductiveDatabase(state, outer_theorems=inference_rule_sets['basic'] + inference_rule_sets['complex'])
        algebraic_system = AlgebraicSystem(state)
        proof_generator = ProofGenerator(state)
        engine = Engine(state, deductive_database, algebraic_system, proof_generator)

        t0 = time.time()
        engine.search()
        t = time.time() - t0
        result = state.complete()
        if result:
            assert abs((sympify(result).evalf() - sympify(solution).evalf()) / (sympify(solution).evalf() + 1e-4)) < 1e-2
            engine.generate_proof()
            return idx, True, f"[{idx}] Solved in {t:.2f}s"
        else:
            return idx, False, f"[{idx}] Not solved in {t:.2f}s"
    except Exception as e:
        return idx, False, f"[{idx}] Failed: {e}"

class TestBenchmarks(unittest.TestCase):
    def test_geometry3k(self):
        start_idx, end_idx = 2401, 3001
        timeout_sec = 600
        max_workers = multiprocessing.cpu_count() // 2 or 1
        total = end_idx - start_idx
        solved_count = 0
        results = []

        log_path = "geometry3k_results.log"
        with open(log_path, "w") as logfile:
            def log(msg):
                logfile.write(msg + "\n")
                logfile.flush()

            with ProcessPoolExecutor(max_workers=max_workers) as executor:
                futures = {executor.submit(run_single_problem, idx): idx for idx in range(start_idx, end_idx+1)}

                for future in tqdm(as_completed(futures, timeout=(timeout_sec + 10) * len(futures)),
                                   total=len(futures), desc="Processing problems"):
                    idx = futures[future]
                    try:
                        result = future.result(timeout=timeout_sec)
                        results.append(result)
                        if result[1]:
                            solved_count += 1
                    except TimeoutError:
                        results.append((idx, False, f"[{idx}] Timeout after {timeout_sec} seconds"))
                    except Exception as e:
                        results.append((idx, False, f"[{idx}] Crashed: {e}"))

            for _, _, message in sorted(results):
                log(message)

            log(f"\n✅ Total Solved: {solved_count} / {total}")

if __name__ == '__main__':
    unittest.main()
