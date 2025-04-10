import unittest
import time
import multiprocessing
from sympy import sympify
from tqdm import tqdm
import logging
from concurrent.futures import ProcessPoolExecutor, as_completed, TimeoutError

from pyeuclid.formalization.state import State
from pyeuclid.formalization.relation import *
from pyeuclid.engine.inference_rule import inference_rule_sets
from pyeuclid.engine.deductive_database import DeductiveDatabase
from pyeuclid.engine.algebraic_system import AlgebraicSystem
from pyeuclid.engine.proof_generator import ProofGenerator
from pyeuclid.engine.engine import Engine

def run_single_problem(problem):
    state = State()
    state.logger.setLevel(logging.INFO)
    if isinstance(problem, str):
        state.load_problem_from_text(problem, f'diagrams/JGEX-AG-231/test.jpg')
    else:
        namespace = {}
        with open(f'data/Geometry3K/{problem}/problem.py', "r") as file:
            exec(file.read(), namespace)
        conditions = namespace.get("conditions")
        goal = namespace.get("goal")
        solution = namespace.get("solution")
        diagrammatic_relations = namespace.get("diagrammatic_relations")
        state.try_complex = True
        state.load_problem(conditions=conditions, goal=goal)
        state.add_relations(diagrammatic_relations)

    deductive_database = DeductiveDatabase(state, outer_theorems=inference_rule_sets['basic'] + inference_rule_sets['complex'])
    algebraic_system = AlgebraicSystem(state)
    proof_generator = ProofGenerator(state)
    engine = Engine(state, deductive_database, algebraic_system)

    t0 = time.time()
    engine.search()
    t = time.time() - t0
    result = state.complete()
    if result is not None:
        proof_generator.generate_proof()
        proof_generator.show_proof()
        assert result is True or abs((sympify(result).evalf() - sympify(solution).evalf()) / (sympify(solution).evalf() + 1e-4)) < 1e-2
        print(f"Solved in {t:.2f}s")
    else:
        print(f"Not solved in {t:.2f}s")

if __name__ == '__main__':
    run_single_problem("a b c = triangle a b c; m = midpoint m b a; o = circle o a b c; n = on_line n o m, on_circle n o a ? eqangle c a c n c n c b")
