import time
from sympy import sympify
import sympy
import logging
import argparse

from pyeuclid.formalization.state import State
from pyeuclid.formalization.relation import *
from pyeuclid.formalization.construction_rule import *
from pyeuclid.formalization.utils import *
from pyeuclid.engine.inference_rule import inference_rule_sets
from pyeuclid.engine.deductive_database import DeductiveDatabase
from pyeuclid.engine.algebraic_system import AlgebraicSystem
from pyeuclid.engine.proof_generator import ProofGenerator
from pyeuclid.engine.engine import Engine

parser = argparse.ArgumentParser()
parser.add_argument('--problem-id', type=int, help="Problem id from InterGPS dataset, refer to data/Geometry3K for examples.", default=2455)
parser.add_argument('--problem-string', type=str, help="A problem string in jgex format, refer to data/JGEX-AG-231.txt for examples.", default=" b = segment a b; c = lc_tangent c b a; d = midpoint d b c; e = on_circle e a b; f = on_line f d e, on_circle f a b ? eqangle e c c d d f f c")   
parser.add_argument('--show-proof', action='store_true')

def run_single_problem(args):
    state = State()
    # state.silent = True
    state.logger.setLevel(logging.INFO)
    if args.problem_string is not None:
        state.load_problem_from_text(args.problem_string, f'diagrams/JGEX-AG-231/test.jpg', resample=True)
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
    deductive_database = DeductiveDatabase(state, outer_theorems=inference_rule_sets['basic'])
    algebraic_system = AlgebraicSystem(state)
    proof_generator = ProofGenerator(state)
    engine = Engine(state, deductive_database, algebraic_system)
    t0 = time.time()
    engine.run()
    # while True:
    #     # 001. BC ∥ FG [04] & BG ∥ CF [05] ⇒  ∠FGB = ∠BCF [07]
    #     # 002. BG ∥ CF [05] ⇒  ∠FBG = ∠BFC [08]
    #     # 003. ∠FGB = ∠BCF [07] & ∠FBG = ∠BFC [08] (Similar Triangles)⇒  BG = FC [09]
    #     # 004. CB = BG [02] & BG = FC [09] ⇒  CF = CB [10]
    #     # 005. BC ⟂ BG [03] & BC ∥ FG [04] ⇒  GF ⟂ GB [11]
    #     # 006. AC ⟂ CD [01] & CD ∥ AE [06] ⇒  CA ⟂ AE [12]
    #     # 007. GF ⟂ GB [11] & CA ⟂ AE [12] ⇒  ∠(FG-AE) = ∠(BG-AC) [13]
    #     # 008. GF ⟂ GB [11] & CA ⟂ AE [12] ⇒  ∠FGB = ∠CAE [14]
    #     # 009. ∠(FG-AE) = ∠(BG-AC) [13] & BC ∥ FG [04] & AE ∥ CD [06] & BG ∥ CF [05] ⇒  ∠ACF = ∠DCB [15]
    #     # 010. AC = CD [00] & CF = CB [10] & ∠ACF = ∠DCB [15] (SAS)⇒  ∠(AF-BD) = ∠FCB [16]
    #     # 011. AC = CD [00] & CF = CB [10] & ∠ACF = ∠DCB [15] (SAS)⇒  ∠DCA = ∠(BD-AF) [17]
    #     # 012. ∠(AF-BD) = ∠FCB [16] & CF ∥ BG [05] & ∠FGB = ∠CAE [14] & BC ∥ FG [04] & AE ∥ CD [06] & ∠DCA = ∠(BD-AF) [17] ⇒  DB ⟂ FA
    #     engine.search(depth=1)
    #     p1 = state.check_conditions(Length(Point('b'),Point('g'))-Length(Point('f'),Point('c')))
    #     p2 = state.check_conditions(Angle(Point('f'),Point('g'),Point('b'))-Angle(Point('c'),Point('a'),Point('e')))
    #     p3 = state.check_conditions(Angle(Point('a'),Point('c'),Point('f'))-Angle(Point('d'),Point('c'),Point('b')))
    #     print(p1, p2, p3)
    #     input()
    t = time.time() - t0
    result = state.complete()
    if result is not None:
        if args.show_proof:
            t0 = time.time()
            with Timeout(600):
                proof_generator.run()
                proof = proof_generator.format_proof()
                max_cond_num = 0
                acc_cond_num = 0
                step = 0
                proof_generator.show_proof()
            
            # print(f'proof genratation runs in {time.time()-t0}')
            # print(f'Proof steps: ', step)
            # print(f'Max condition number: ', max_cond_num)
            # print(f'Average condition number: ', acc_cond_num / step)
        print(f"Solved in {t:.2f}s")
    else:
        print(f"Not solved in {t:.2f}s")

if __name__ == '__main__':
    args = parser.parse_args()
    run_single_problem(args)
