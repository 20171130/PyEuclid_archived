import time
from sympy import sympify
import sympy
import logging
import argparse

from stopit import ThreadingTimeout as TT

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
parser.add_argument('--problem-id', type=int, help="Problem id from InterGPS dataset, refer to data/Geometry3K for examples.", default=2455)
parser.add_argument('--problem-string', type=str, help="A problem string in jgex format, refer to data/JGEX-AG-231.txt for examples.", default="a b = segment a b; d = midpoint d b a; c = on_tline c a a b; e = on_circle e c a; f = on_line f d e, on_circle f c a; g = on_circle g c f, on_line g f b; h = on_line h b e, on_circle h c a ? para a b g h")   
parser.add_argument('--show-proof', action='store_true')

def run_single_problem(args):
    state = State()
    # state.silent = True
    state.logger.setLevel(logging.INFO)
    if args.problem_string is not None:
        state.load_problem_from_text(args.problem_string, f'diagrams/JGEX-AG-231/test.jpg')
        state.diagram.draw_diagram()
    else:
        namespace = {}
        with open(f'data/Geometry3K/{args.problem_id}/problem.py', "r") as file:
            exec(file.read(), namespace)
        conditions = namespace.get("conditions")
        goal = namespace.get("goal")
        solution = namespace.get("solution")
        diagrammatic_relations = namespace.get("diagrammatic_relations")
        state.load_problem(conditions=conditions, goal=goal)
        state.add_conditions(diagrammatic_relations)
    deductive_database = DeductiveDatabase(state)
    algebraic_system = AlgebraicSystem(state)
    proof_generator = ProofGenerator(state)
    proof_generator.max_equation_length_perstep = 20
    engine = Engine(state, deductive_database, algebraic_system)
    # Length_b_d/Length_d_f - Length_d_e/Length_b_d
    state.goal = Length(Point('b'),Point('d'))/Length(Point('d'),Point('f')) - Length(Point('d'),Point('e'))/Length(Point('b'),Point('d'))
    prop1 = Length(Point('b'),Point('d'))/Length(Point('d'),Point('f')) - Length(Point('d'),Point('e'))/Length(Point('b'),Point('d'))
    prop2 = Length(Point('a'),Point('d'))/Length(Point('d'),Point('f')) - Length(Point('d'),Point('e'))/Length(Point('a'),Point('d'))
    t0 = time.time()
    engine.run()
    t = time.time() - t0
    result = state.complete()
    print(state.check_conditions(prop1), state.check_conditions(prop2))
    # Length_a_d - Length_b_d & Length_a_d/Length_d_f - Length_d_e/Length_a_d => Length_b_d/Length_d_f - Length_d_e/Length_b_d
    if result is not None:
        print(f"Solved in {t:.2f}s")
        if args.show_proof:
            t0 = time.time()
            proof_generator.run()
            proof_generator.show_proof()
            print(f"Proof generated in {time.time()-t0:.2f}s")
    else:
        print(f"Not solved in {t:.2f}s")
        breakpoint()

if __name__ == '__main__':
    args = parser.parse_args()
    run_single_problem(args)
