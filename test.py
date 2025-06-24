import unittest
import time
import shutil

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
            os.makedirs(f'results/JGEX-AG-231/{idx+1}/', exist_ok=True)
            state = State()
            state.silent = True
            if world_size > 1:
                state.silent = True
            try:
                state.load_problem_from_text(text, f'diagrams/JGEX-AG-231/{idx+1}.jpg')
                shutil.copy(f"diagrams/JGEX-AG-231/{idx+1}.jpg", f"results/JGEX-AG-231/{idx+1}/diagram.jpg")
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
                    t0 = time.time()
                    proof = None
                    with TT(600):
                        proof_generator.run()
                        proof = proof_generator.get_proof()
                        proof_str = proof_generator.get_proof_str()
                        max_cond_num = 0
                        acc_cond_num = 0
                        for (conditions, theorem, conclusion) in proof:
                            max_cond_num = max(max_cond_num, len(conditions))
                            acc_cond_num += len(conditions)
                    
                    if proof is not None:
                        print(f'{idx} proof generation runs in {time.time()-t0}')
                        with open(f'results/JGEX-AG-231/{idx+1}/proof.txt', 'w+') as f:
                            f.write(proof_str)
                        print(f'Proof steps: ', len(proof))
                        print(f'Max condition number: ', max_cond_num)
                        print(f'Average condition number: ', acc_cond_num / len(proof) if len(proof) > 0 else 0)
                    else:
                        print(f'{idx} proof generation fails {time.time()-t0}')
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