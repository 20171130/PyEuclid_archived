import time
from sympy import sympify
import sympy
import logging
from stopit import ThreadingTimeout as Timeout
import argparse

from pyeuclid.formalization.state import State
from pyeuclid.formalization.relation import *
from pyeuclid.engine.inference_rule import inference_rule_sets
from pyeuclid.engine.deductive_database import DeductiveDatabase
from pyeuclid.engine.algebraic_system import AlgebraicSystem
from pyeuclid.engine.proof_generator import ProofGenerator
from pyeuclid.engine.engine import Engine

parser = argparse.ArgumentParser()
parser.add_argument('--problem-id', type=int, help="Problem id from InterGPS dataset, refer to data/Geometry3K for examples.", default=2455)
parser.add_argument('--problem-string', type=str, help="A problem string in jgex format, refer to data/JGEX-AG-231.txt for examples.", default="r s = segment r s; t = mirror t r s; o = on_bline o r s; j = on_circle j o s; o1 = circle o1 j s t; a = on_tline a r o r, on_circle a o1 s; b = on_tline b r o r, on_circle b o1 s; k = on_line k j a, on_circle k o s ? perp k t o1 t")   
parser.add_argument('--show-proof', action='store_true')

def run_single_problem(args):
    state = State()
    state.silent = True
    state.logger.setLevel(logging.INFO)
    if args.problem_string is not None:
        state.load_problem_from_text(args.problem_string, f'diagrams/JGEX-AG-231/test.jpg')
    else:
        namespace = {}
        with open(f'data/Geometry3K/{args.problem_id}/problem.py', "r") as file:
            exec(file.read(), namespace)
        conditions = namespace.get("conditions")
        goal = namespace.get("goal")
        solution = namespace.get("solution")
        diagrammatic_relations = namespace.get("diagrammatic_relations")
        state.load_problem(conditions=conditions, goal=goal)
        state.add_relations(diagrammatic_relations)
    deductive_database = DeductiveDatabase(state, outer_theorems=inference_rule_sets['basic'])
    algebraic_system = AlgebraicSystem(state)
    proof_generator = ProofGenerator(state)
    engine = Engine(state, deductive_database, algebraic_system)
    t0 = time.time()
    engine.search()
    t = time.time() - t0
    result = state.complete()
    if result is not None:
        if args.show_proof:
            proof_generator.generate_proof()
            proof_generator.show_proof()
        print(f"Solved in {t:.2f}s")
    else:
        print(f"Not solved in {t:.2f}s")

if __name__ == '__main__':
    args = parser.parse_args()
    run_single_problem(args)
