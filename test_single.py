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
parser.add_argument('--problem-id', type=int, help="Problem id from InterGPS dataset, refer to data/Geometry3K for examples.", default=2455)
parser.add_argument('--problem-string', type=str, default="a b c = triangle a b c; m = free m; n = on_aline n a c b a m; q = foot q m a b; p = foot p m a c ? perp a n p q")
parser.add_argument('--show-proof', action='store_true')

def run_single_problem(args):
    utils.MAX_DIAGRAM_ATTEMPTS = None
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
            proof_generator.show_proof()
            constructions = proof_generator.source_constructions[state.goal]
            print([str(c) for c in constructions])
            if isinstance(state.goal, Relation):
                points = state.goal.get_points()
            else:
                points_list = get_points_and_symbols(state.goal)[0]
                points = [p for points in points_list for p in points]
            target_points = set(points)
            print('target', target_points)
            output_to_constructions = defaultdict(list)
            for c in constructions:
                for out in c.outputs:
                    output_to_constructions[out].append(c)

            required = set()
            seen_points = set()

            def mark_required(point):
                if point in seen_points:
                    return
                seen_points.add(point)

                for c in output_to_constructions[point]:
                    if c not in required:
                        required.add(c)
                        for inp in c.inputs:
                            mark_required(inp)
            
            for point in target_points:
                mark_required(point)
            
            input_points = set()
            output_points = set()
            required_constructions = [c for c in constructions if c in required]
            auxilary_contructions = [c for c in constructions if c not in required]
            print([str(c) for c in required_constructions])
            print([str(c) for c in auxilary_contructions])
            print(f"Proof generated in {time.time()-t0:.2f}s")
    else:
        print(f"Not solved in {t:.2f}s")

if __name__ == '__main__':
    args = parser.parse_args()
    run_single_problem(args)
