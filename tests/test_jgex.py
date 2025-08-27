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
        texts = parse_texts_from_file('data/JGEX-AG-231.txt')
        for idx, text in enumerate(texts):
            if not idx%world_size == rank:
                continue
            result_dir = f"results/JGEX-AG-231/{idx+1}/"
            os.makedirs(result_dir, exist_ok=True)
            state = State()
            state.silent = True
            if world_size > 1:
                state.silent = True
            try:
                diagram_path = os.path.join(result_dir, "diagram.jpg")
                state.load_problem_from_text(text, str(diagram_path))
                deductive_database = DeductiveDatabase(state)
                algebraic_system = AlgebraicSystem(state)
                proof_generator = ProofGenerator(state)
                proof_generator.max_equation_length_perstep = None
                engine = Engine(state, deductive_database, algebraic_system)
                t = time.time()
                with TT(1200):
                    engine.run()
                t = time.time() - t
                if state.complete() is not None:
                    print(f"{idx} solved in {t} seconds")
                    t0 = time.time()
                    proof = None
                    with TT(1200):
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
                        proof_path = os.path.join(result_dir, "proof.txt")
                        with open(proof_path, 'w+') as f:
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


if __name__ == '__main__':
    unittest.main()