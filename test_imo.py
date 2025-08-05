import unittest
import time
import shutil

import os
from sympy import sympify

import pyeuclid.formalization.utils as utils
from pyeuclid.formalization.state import State
from pyeuclid.formalization.relation import *
from pyeuclid.formalization.translation import parse_texts_from_file
from pyeuclid.formalization.utils import Timeout
from pyeuclid.engine.inference_rule import inference_rule_sets
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
        texts = parse_texts_from_file('data/IMO-AG-30.txt')
        for idx, text in enumerate(texts):
            if not idx%world_size == rank:
                continue
            state = State()
            state.silent = True
            if world_size > 1:
                state.silent = True
            try:
                state.load_problem_from_text(text, f'diagrams/IMO-AG-30/{idx+1}.jpg')
                os.makedirs(f'results/IMO-AG-30/{idx+1}/', exist_ok=True)
                shutil.copy(f"diagrams/IMO-AG-30/{idx+1}.jpg", f"results/IMO-AG-30/{idx+1}/diagram.jpg")
                deductive_database = DeductiveDatabase(state)
                algebraic_system = AlgebraicSystem(state)
                proof_generator = ProofGenerator(state)
                proof_generator.max_equation_length_perstep = None
                engine = Engine(state, deductive_database, algebraic_system)
                t0 = time.time()
                t1 = None
                with Timeout(5400):
                    engine.search()
                    t1 = time.time()
                    if state.complete() is not None:
                        print(f"{idx} solved in {t1-t0} seconds")
                        proof_generator.run()
                        proof_str = proof_generator.get_proof_str()
                        print(f'{idx} proof generation runs in {time.time()-t1}')
                        with open(f'results/IMO-AG-30/{idx+1}/new_proof.txt', 'w+') as f:
                            f.write(proof_str)
                    else:
                        print(f"{idx} unsolved in {t1-t0} seconds")
                if t1 is None:
                    print(f"{idx} unsolved in 5400 seconds")
            except BaseException as e:
                if isinstance(e, KeyboardInterrupt):
                    exit()
                print(f"{idx} error {text}")
                print(e)
                print(traceback.format_exc())
                

if __name__ == '__main__':
    unittest.main()