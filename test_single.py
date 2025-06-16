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
parser.add_argument('--problem-string', type=str, help="A problem string in jgex format, refer to data/JGEX-AG-231.txt for examples.", default="a b c = triangle a b c; d = foot d a b c; q = foot q d a b; p = foot p d a c ? cyclic b q p c")   
parser.add_argument('--show-proof', action='store_true')

def run_single_problem(args):
    state = State()
    # state.silent = True
    state.logger.setLevel(logging.INFO)
    if args.problem_string is not None:
        state.load_problem_from_text(args.problem_string, f'diagrams/JGEX-AG-231/test.jpg')
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
    # engine.run()
    while True:
        engine.search(depth=1)
    # 001. P,C,A are collinear [03] & B,Q,A are collinear [01] & DQ ⟂ AB [02] & DP ⟂ AC [04] ⇒  ∠APD = ∠AQD [05]
    # 002. ∠APD = ∠AQD [05] ⇒  P,Q,D,A are concyclic [06]
    # 003. P,Q,D,A are concyclic [06] ⇒  ∠PQD = ∠PAD [07]
    # 004. B,Q,A are collinear [01] & DQ ⟂ AB [02] ⇒  QD ⟂ BQ [08]
    # 005. QD ⟂ BQ [08] & AD ⟂ BC [00] ⇒  ∠QDA = ∠QBC [09]
    # 006. B,Q,A are collinear [01] & P,C,A are collinear [03] & ∠PQD = ∠PAD [07] & ∠QDA = ∠QBC [09] ⇒  ∠QBC = ∠QPC [10]
    # 007. ∠QBC = ∠QPC [10] ⇒  B,Q,P,C are concyclic
        p1 = state.check_conditions(Angle(Point('a'),Point('p'),Point('d'))-Angle(Point('a'),Point('q'),Point('d')))
        p2 = state.check_conditions(Concyclic(Point('p'),Point('q'),Point('d'),Point('a')))
        p3 = state.check_conditions(Angle(Point('p'),Point('q'),Point('d'))-Angle(Point('p'),Point('a'),Point('d')))
        p4 = state.check_conditions(Perpendicular(Point('q'),Point('d'),Point('b'),Point('q')))
        p5 = state.check_conditions(Angle(Point('q'),Point('d'),Point('a'))-Angle(Point('q'),Point('b'),Point('c')))
        p6 = state.check_conditions(Angle(Point('q'),Point('b'),Point('c'))+Angle(Point('q'),Point('p'),Point('c'))-pi)
        p7 = state.check_conditions(Concyclic(Point('b'),Point('q'),Point('p'),Point('c')))
        print(p1, p2, p3, p4, p5, p6,p7)
        for cond in AlphaGeometry5b(Point('c'),Point('q'),Point('b'),Point('p')).condition():
            print(cond, state.check_conditions(cond))
        print(AlphaGeometry5b(Point('c'),Point('q'),Point('b'),Point('p')).conclusion())
        print(state.angles.equivalence_classes())
        breakpoint()
        
    t = time.time() - t0
    result = state.complete()
    if result is not None:
        if args.show_proof:
            t0 = time.time()
            with TT(600):
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
