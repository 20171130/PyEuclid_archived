import time
import logging
import argparse
import sympy
from itertools import combinations
from sympy.core.relational import Relational

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
parser.add_argument('--problem-string', type=str, default="a b = segment a b; c = on_circle c a b; f = on_circle f a b; e = on_line e b c, on_dia e f a; g = intersection_lc g e a f; d = lc_tangent d b a, lc_tangent d c a; h = on_line h c d, on_line h e f; i = on_line i e f, on_line i b d ? cong c h b i")
parser.add_argument('--problem-id', type=int, help="Problem id from InterGPS dataset, refer to data/Geometry3K for examples.")
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
        conditions = [expr if isinstance(expr, Relation) else sympy.nsimplify(expr, rational=True, tolerance=1e-12) for expr in conditions]
        goal = namespace.get("goal")
        solution = namespace.get("solution")
        diagrammatic_relations = namespace.get("diagrammatic_relations")
        state.load_problem(conditions=conditions, goal=goal)
        for relation in diagrammatic_relations:
            if isinstance(relation, (SameSide, OppositeSide)):
                pts = relation.get_points()
                pts1 = [pts[0]] + pts[2:]
                pts2 = pts[1:]
                if any(Collinear(*trip) in state.relations for trip in [pts1, pts2]):
                    print(relation)
                    continue
            state.add_conditions(relation)
        deductive_database = DeductiveDatabase(state, outer_theorems=inference_rule_sets["basic"]+inference_rule_sets['complex'])
    else:
        state.load_problem_from_text(args.problem_string, f'diagrams/test.jpg')
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
        breakpoint()
    else:
        breakpoint()
        print(f"Not solved in {t:.2f}s")

if __name__ == '__main__':
    args = parser.parse_args()
    run_single_problem(args)