import time
import logging
import argparse
import sympy

import pyeuclid.formalization.utils as utils
from pyeuclid.formalization.state import State
from pyeuclid.formalization.relation import *
from pyeuclid.formalization.construction_rule import *
from pyeuclid.formalization.utils import *
from pyeuclid.engine.inference_rule import *
from pyeuclid.engine.deductive_database import DeductiveDatabase
from pyeuclid.engine.algebraic_system import AlgebraicSystem
from pyeuclid.engine.proof_generator import ProofGenerator
from pyeuclid.engine.engine import Engine

parser = argparse.ArgumentParser()
parser.add_argument('--problem-id', type=int, help="Problem id from InterGPS dataset, refer to data/Geometry3K for examples.", default=2425)
# A,B,C = construct_risos(), D = construct_on_circle(C,A), D = construct_on_line(C,A), E = construct_orthocenter(C,D,B), F = construct_angle_mirror(B,D,C), F = construct_on_circum(E,A,C), G,H = construct_square(E,F)
parser.add_argument('--problem-string', type=str, default="a b = segment a b; c = free c; d = on_bline b c; e = parallelogram c a d e; f = eqdistance f e d b, on_circle f d a ? coll a d f")
parser.add_argument('--show-proof', action='store_true')

def run_single_problem(args):
    utils.MAX_DIAGRAM_ATTEMPTS = None
    state = State()
    # state.silent = True
    state.logger.setLevel(logging.INFO)
    if args.problem_id is not None:
        namespace = {}
        with open(f'data/Geometry3K/{args.problem_id}/problem.py', "r") as file:
            exec(file.read(), namespace)
        conditions = namespace.get("conditions")
        goal = namespace.get("goal")
        solution = namespace.get("solution")
        diagrammatic_relations = namespace.get("diagrammatic_relations")
        state.load_problem(conditions=conditions, goal=goal)
        state.add_conditions(diagrammatic_relations)
        deductive_database = DeductiveDatabase(state, outer_theorems=inference_rule_sets["basic"]+inference_rule_sets['complex'])
    else:
        state.load_problem_from_text(args.problem_string, f'diagrams/JGEX-AG-231/test.jpg', resample=True)
        state.diagram.draw_diagram()
        deductive_database = DeductiveDatabase(state)
    algebraic_system = AlgebraicSystem(state)
    proof_generator = ProofGenerator(state)
    proof_generator.max_equation_length_perstep = None
    engine = Engine(state, deductive_database, algebraic_system)
    t0 = time.time()
    engine.run()
    t = time.time() - t0
    result = state.complete()
    if result is not None:
        print(f"Solved in {t:.2f}s")
        if args.show_proof:
            t0 = time.time()
            proof_generator.run()
            proof_generator.show_proof(verbose=True)
            print(f"Proof generated in {time.time()-t0:.2f}s")
    else:
        # breakpoint()
        print(state.points)
        print(f"Not solved in {t:.2f}s")

if __name__ == '__main__':
    args = parser.parse_args()
    run_single_problem(args)
