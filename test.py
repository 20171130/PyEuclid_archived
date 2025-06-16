import unittest
import time

import os
from sympy import sympify

from stopit import ThreadingTimeout as TT

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
        rank = int(os.environ.get("OMPI_COMM_WORLD_RANK", 0))
        world_size = int(os.environ.get("OMPI_COMM_WORLD_SIZE", 1))
        texts = parse_texts_from_file('data/JGEX-AG-231.txt')
        for idx, text in enumerate(texts):
            if not idx%world_size == rank:
                continue
            state = State()
            state.silent = True
            if world_size > 1:
                state.silent = True
            try:
                state.load_problem_from_text(text, f'diagrams/JGEX-AG-231/{idx+1}.jpg')
                deductive_database = DeductiveDatabase(state)
                algebraic_system = AlgebraicSystem(state)
                proof_generator = ProofGenerator(state)
                engine = Engine(state, deductive_database, algebraic_system)
                t = time.time()
                with TT(600):
                    engine.run()
                t = time.time() - t
                if state.complete() is not None:
                    print(f"{idx} solved in {t} seconds")
                    # t0 = time.time()
                    # with TT(60):
                    #     proof_generator.run()
                #         proof = proof_generator.format_proof()
                #         max_cond_num = 0
                #         acc_cond_num = 0
                #         step = 0
                #         for proof_step in proof:
                #             if not isinstance(proof_step['condition'][0], ConstructionRule):
                #                 step += 1
                #                 def trivial_inference(item):
                #                     for source in getattr(item, "sources", []):
                #                         if type(source) in (DiagramAngle4a, DiagramAngle4b, DiagramAngle2, FlatAngle, PropertyOfTriangle):
                #                             return True
                #                 conditions = [item for item in proof_step['condition'] if not trivial_inference(item)]
                #                 max_cond_num = max(max_cond_num, len(conditions))
                #                 acc_cond_num += len(conditions)
                    
                    # print(idx)
                    # print(f'proof genratation runs in {time.time()-t0}')
                #     print(f'Proof steps: ', step)
                #     print(f'Max condition number: ', max_cond_num)
                #     print(f'Average condition number: ', acc_cond_num / step)
                    # if world_size == 1:
                    #     proof_generator.show_proof()
                else:
                    print(f"{idx} unsolved in {t} seconds")
            except BaseException as e:
                if isinstance(e, KeyboardInterrupt):
                    exit()
                print(f"{idx} error {text}")
                print(e)
                print(traceback.format_exc())
            
    # def test_geometry3k(self):
    #     rank = int(os.environ.get("OMPI_COMM_WORLD_RANK", 0))
    #     world_size = int(os.environ.get("OMPI_COMM_WORLD_SIZE", 1))
    #     for idx in range(2401, 3002):
    #         if not idx%world_size == rank:
    #             continue
    #         if not os.path.isfile(f"data/Geometry3K/{idx}/problem.py"):
    #             continue
    #         namespace = {}
    #         try:
    #             with open(f'data/Geometry3K/{idx}/problem.py', "r") as file:
    #                 exec(file.read(), namespace)
    #             conditions = namespace.get("conditions")
    #             goal = namespace.get("goal")
    #             solution = namespace.get("solution")
    #             diagrammatic_relations = namespace.get("new_diagrammatic_relations")
    #             for i in conditions:
    #                 if isinstance(i, Between):
    #                     diagrammatic_relations.discard(NotCollinear(i.p1,i.p2,i.p3))
    #             state = State()
    #             state.silent = True
    #             state.load_problem(conditions=conditions, goal=goal)
    #             state.add_conditions(list(diagrammatic_relations))
                
    #             deductive_database = DeductiveDatabase(state, outer_theorems=inference_rule_sets['basic']+inference_rule_sets['complex'])
    #             algebraic_system = AlgebraicSystem(state)
    #             proof_generator = ProofGenerator(state)
    #             engine = Engine(state, deductive_database, algebraic_system)

    #             try:
    #                 t = time.time()
    #                 with Timeout(600) as tt:
    #                     engine.search()
    #                 result = state.complete()
    #                 if result is None:
    #                     state.try_complex = True
    #                     engine.deductive_database.closure = False
    #                     with Timeout(600) as tt:
    #                         engine.search()
    #                 t = time.time() - t
    #             except:
    #                 pass
    #             result = state.complete()
                
    #             if result is not None:
    #                 if (result is True or abs((sympify(result).evalf() - sympify(solution).evalf()) / (sympify(solution).evalf() + 1e-4)) < 2e-2):
    #                     print(f"{idx} solved in {t} seconds {state.try_complex}")
    #                 else:
    #                     print(f"{idx} wrong solution in {t} seconds")
    #                 proof_generator.generate_proof()
    #                 if world_size == 1:
    #                     proof_generator.show_proof()
    #             else:
    #                 print(f"{idx} unsolved in {t} seconds")
    #         except BaseException as e:
    #             if isinstance(e, KeyboardInterrupt):
    #                 exit()
    #             print(f"{idx} error {e}")
    #             print(traceback.format_exc())

if __name__ == '__main__':
    unittest.main()