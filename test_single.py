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
parser.add_argument('--problem-string', type=str, help="A problem string in jgex format, refer to data/JGEX-AG-231.txt for examples.", default="a b c = triangle a b c; h = orthocenter h a b c; m = on_line m h b, on_line m a c; n = on_line n h c, on_line n a b; w = on_line w b c; o1 = circle o1 b n w; o2 = circle o2 c m w; x = on_line x o1 w, on_circle x o1 w; y = on_line y o2 w, on_circle y o2 w ? coll x h y")   
parser.add_argument('--show-proof', action='store_true')

def run_single_problem(args):
    state = State()
    # state.silent = True
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

    p1 = state.check_conditions(Angle(Point('c'),Point('b'),Point('m'))-Angle(Point('h'),Point('a'),Point('m')))
    p2 = state.check_conditions(Angle(Point('h'),Point('n'),Point('a'))-Angle(Point('x'),Point('n'),Point('w')))
    p3 = state.check_conditions(Angle(Point('h'),Point('a'),Point('n'))-Angle(Point('x'),Point('w'),Point('n')))
    p4 = state.check_conditions(Angle(Point('m'),Point('h'),Point('a'))-Angle(Point('m'),Point('y'),Point('w')))
    p5 = state.check_conditions(Angle(Point('w'),Point('m'),Point('a'))-Angle(Point('y'),Point('m'),Point('h')))
    p6 = state.check_conditions(Perpendicular(Point('y'),Point('h'),Point('a'),Point('w')))
    # p2 = state.check_conditions(Angle(Point('d'),Point('r'),Point('q'))-Angle(Point('d'),Point('b'),Point('c')))
    # p3 = state.check_conditions(Angle(Point('d'),Point('r'),Point('q'))-Angle(Point('d'),Point('c'),Point('b')))
    print(p1,p2,p3,p4,p5,p6)
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
