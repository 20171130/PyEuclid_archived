import unittest
import time

import os
from sympy import sympify

from pyeuclid.formalization.translation import parse_texts_from_file
from pyeuclid.formalization.state import State
from pyeuclid.formalization.relation import *
from pyeuclid.engine.inference_rule import inference_rule_sets
from pyeuclid.engine.deductive_database import DeductiveDatabase
from pyeuclid.engine.algebraic_system import AlgebraicSystem
from pyeuclid.engine.proof_generator import ProofGenerator
from pyeuclid.engine.engine import Engine

class TestBenchmarks(unittest.TestCase):
    def test_jgex_ag_231(self):
        rank = int(os.environ.get("OMPI_COMM_WORLD_RANK", 0))
        world_size = int(os.environ.get("OMPI_COMM_WORLD_SIZE", 1))
        texts = parse_texts_from_file('data/JGEX-AG-231.txt')
        for idx, text in enumerate(texts):
            if not idx%world_size == rank:
                continue
            state = State()
            if world_size > 1:
                state.silent = True
            try:
                state.load_problem_from_text(text, f'diagrams/JGEX-AG-231/{idx+1}.jpg')
                deductive_database = DeductiveDatabase(state)
                algebraic_system = AlgebraicSystem(state)
                proof_generator = ProofGenerator(state)
                engine = Engine(state, deductive_database, algebraic_system, proof_generator)
                t = time.time()
                engine.search()
                t = time.time() - t
                if state.complete() is not None:
                    print(f"Solved in {t} seconds")
                    engine.proof_generartion()
                else:
                    print(f"Not solved in {t} seconds")
            except BaseException as e:
                print(f"Error {idx} {text} {e}")
            
    # def test_geometry3k(self):
    #     for idx in range(2401, 3002):
    #         print(idx)
    #         namespace = {}
    #         try:
    #             with open(f'data/Geometry3K/{idx}/problem.py', "r") as file:
    #                 exec(file.read(), namespace)
    #             conditions = namespace.get("conditions")
    #             goal = namespace.get("goal")
    #             solution = namespace.get("solution")
    #             diagrammatic_relations = namespace.get("diagrammatic_relations")
    #         except:
    #             continue
            
    #         state = State()
    #         state.try_complex = True
    #         state.silent = True
    #         state.load_problem(conditions=conditions, goal=goal)
    #         state.add_relations(diagrammatic_relations)
            
    #         deductive_database = DeductiveDatabase(state, outer_theorems=inference_rule_sets['basic']+inference_rule_sets['complex'])
    #         algebraic_system = AlgebraicSystem(state)
    #         proof_generator = ProofGenerator(state)
    #         engine = Engine(state, deductive_database, algebraic_system, proof_generator)

    #         t = time.time()
    #         engine.search()
    #         t = time.time() - t
    #         result = state.complete()
            
    #         if result:
    #             assert abs((sympify(result).evalf() - sympify(solution).evalf()) / (sympify(solution).evalf() + 1e-4)) < 1e-2
    #             print(f"Solved in {t} seconds")
    #             engine.proof_generartion()
    #         else:
    #             print(f"Not solved in {t} seconds")
            

if __name__ == '__main__':
    unittest.main()