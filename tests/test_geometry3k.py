import unittest
import time
import shutil

import os
from sympy import sympify
from collections import Counter

from stopit import ThreadingTimeout as TT

import pyeuclid.formalization.utils as utils
from pyeuclid.formalization.state import State
from pyeuclid.formalization.relation import *
from pyeuclid.formalization.translation import parse_texts_from_file
from pyeuclid.formalization.utils import Timeout, TimeoutException
from pyeuclid.formalization.construction_rule import *
from pyeuclid.engine.inference_rule import *
from pyeuclid.engine.deductive_database import DeductiveDatabase
from pyeuclid.engine.algebraic_system import AlgebraicSystem
from pyeuclid.engine.proof_generator import ProofGenerator
from pyeuclid.engine.engine import Engine

import traceback

class TestBenchmarks(unittest.TestCase):
    def test_jgex_ag_231(self):
        utils.MAX_DIAGRAM_ATTEMPTS = None
        rank = int(os.environ.get("OMPI_COMM_WORLD_RANK", 0))
        world_size = int(os.environ.get("OMPI_COMM_WORLD_SIZE", 1))
        problem_ids = range(2401, 3002)
        for idx in problem_ids:
            if not idx%world_size == rank:
                continue
            result_dir = f"results/Geometry3K/{idx+1}/"
            os.makedirs(result_dir, exist_ok=True)
            state = State()
            state.silent = True
            if world_size > 1:
                state.silent = True
            try:
                namespace = {}
                with open(f'data/Geometry3K/{idx}/problem.py', "r") as file:
                    exec(file.read(), namespace)
                conditions = namespace.get("conditions")
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
                            continue
                    state.add_conditions(relation)
                # state.add_conditions(diagrammatic_relations)
                deductive_database = DeductiveDatabase(state, outer_theorems=inference_rule_sets["basic"]+inference_rule_sets['complex'])
                algebraic_system = AlgebraicSystem(state)
                proof_generator = ProofGenerator(state)
                proof_generator.max_equation_length_perstep = None
                engine = Engine(state, deductive_database, algebraic_system)
                t = time.time()
                with TT(1200):
                    engine.run()
                t = time.time() - t
                result = state.complete()
                if result is not None:
                    if result is True or abs((sympify(result).evalf() - sympify(solution).evalf()) / (sympify(solution).evalf() + 1e-4)) < 2e-2:
                        print(f"{idx} solved in {t} seconds")
                        t0 = time.time()
                        proof_str = None
                        with TT(1200):
                            proof_generator.run()
                            proof_str = proof_generator.get_proof_str()
                        
                        if proof_str is not None:
                            print(f'{idx} proof generation runs in {time.time()-t0}')
                            proof_path = os.path.join(result_dir, "proof.txt")
                            with open(proof_path, 'w+') as f:
                                f.write(proof_str)
                        else:
                            print(f'{idx} proof generation fails {time.time()-t0}')
                    else:
                        print(f"{idx} has a wrong solution in {t} seconds")
                else:
                    print(f"{idx} unsolved in {t} seconds")
            except BaseException as e:
                if isinstance(e, KeyboardInterrupt):
                    exit()
                print(f"{idx} error")
                print(e)
                print(traceback.format_exc())


if __name__ == '__main__':
    unittest.main()