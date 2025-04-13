import unittest
import time

import os
from sympy import sympify

from pyeuclid.formalization.state import State
from pyeuclid.formalization.relation import *
from pyeuclid.formalization.translation import parse_texts_from_file
from pyeuclid.engine.inference_rule import inference_rule_sets
from pyeuclid.engine.deductive_database import DeductiveDatabase
from pyeuclid.engine.algebraic_system import AlgebraicSystem
from pyeuclid.engine.proof_generator import ProofGenerator
from pyeuclid.engine.engine import Engine
import traceback
from stopit import ThreadingTimeout as Timeout

class TestBenchmarks(unittest.TestCase):
    # def test_jgex_ag_231(self):
    #     rank = int(os.environ.get("OMPI_COMM_WORLD_RANK", 0))
    #     world_size = int(os.environ.get("OMPI_COMM_WORLD_SIZE", 1))
    #     texts = parse_texts_from_file('data/JGEX-AG-231.txt')
    #     for idx, text in enumerate(texts):
    #         if not idx%world_size == rank:
    #             continue
    #         state = State()
    #         if world_size > 1:
    #             state.silent = True
    #         try:
    #             state.load_problem_from_text(text, f'diagrams/JGEX-AG-231/{idx+1}.jpg')
    #             deductive_database = DeductiveDatabase(state)
    #             algebraic_system = AlgebraicSystem(state)
    #             proof_generator = ProofGenerator(state)
    #             engine = Engine(state, deductive_database, algebraic_system)
    #             t = time.time()
    #             engine.search()
    #             t = time.time() - t
    #             if state.complete() is not None:
    #                 print(f"{idx} solved in {t} seconds")
    #                 proof_generator.generate_proof()
    #                 if world_size == 1:
    #                     proof_generator.show_proof()
    #             else:
    #                 print(f"{idx} unsolved in {t} seconds")
    #         except BaseException as e:
    #             if isinstance(e, KeyboardInterrupt):
    #                 exit()
    #             print(f"{idx} error {text} {e}")
    #             print(traceback.format_exc())
            
    def test_geometry3k(self):
        rank = int(os.environ.get("OMPI_COMM_WORLD_RANK", 0))
        world_size = int(os.environ.get("OMPI_COMM_WORLD_SIZE", 1))
        for idx in [2796]:
            if not idx%world_size == rank:
                continue
            if not os.path.isfile(f"data/Geometry3K/{idx}/problem.py"):
                continue
            namespace = {}
            try:
                with open(f'data/Geometry3K/{idx}/problem.py', "r") as file:
                    exec(file.read(), namespace)
                conditions = namespace.get("conditions")
                goal = namespace.get("goal")
                solution = namespace.get("solution")
                diagrammatic_relations = namespace.get("new_diagrammatic_relations")
                state = State()
                state.silent = False
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
                
                deductive_database = DeductiveDatabase(state, outer_theorems=inference_rule_sets['basic']+inference_rule_sets['complex'])
                algebraic_system = AlgebraicSystem(state)
                proof_generator = ProofGenerator(state)
                engine = Engine(state, deductive_database, algebraic_system)

                t = time.time()
                # with Timeout(600) as tt:
                #     engine.search()
                # result = state.complete()
                if True:
                    state.try_complex = True
                    engine.deductive_database.closure = False
                    with Timeout(600) as tt:
                        engine.search()
                    result = state.complete()
                print(result)

                t = time.time() - t
                
                
                if result is not None:
                    if (result is True or abs((sympify(result).evalf() - sympify(solution).evalf()) / (sympify(solution).evalf() + 1e-4)) < 1e-2):
                        print(f"{idx} solved in {t} seconds")
                    else:
                        print(f"{idx} wrong solution in {t} seconds")
                    proof_generator.generate_proof()
                    if world_size == 1:
                        proof_generator.show_proof()
                else:
                    print(f"{idx} unsolved in {t} seconds")
            except BaseException as e:
                if isinstance(e, KeyboardInterrupt):
                    exit()
                print(f"{idx} error {e}")
                print(traceback.format_exc())

if __name__ == '__main__':
    unittest.main()