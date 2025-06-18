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
parser.add_argument('--problem-string', type=str, help="A problem string in jgex format, refer to data/JGEX-AG-231.txt for examples.", default="a b = segment a b; d = midpoint d b a; f = on_circle f d a; c = intersection_lt c a b f d f; e = midpoint e c a; g = on_tline g b a b, on_circle g e a ? eqangle f c f g g f g c")   
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
    #     engine.search(depth=1)
        # 001. CE = CA [03] & CH = CA [08] & CG = CF [07] & CF = CA [04] ⇒  G,F,E,H are concyclic [10]
        # 002. G,F,E,H are concyclic [10] ⇒  ∠GFE = ∠GHE [11]
        # 003. CE = CA [03] & CF = CA [04] ⇒  C is the circumcenter of \Delta AEF [12]
        # 004. D,A,B are collinear [00] & AC ⟂ AB [02] ⇒  CA ⟂ AD [13]
        # 005. C is the circumcenter of \Delta AEF [12] & CA ⟂ AD [13] ⇒  ∠DAE = ∠AFE [14]
        # 006. D,E,F are collinear [05] & D,A,B are collinear [00] & ∠DAE = ∠AFE [14] ⇒  ∠AFD = ∠DAE [15]
        # 007. D,A,B are collinear [00] & D,E,F are collinear [05] ⇒  ∠ADF = ∠ADE [16]
        # 008. ∠AFD = ∠DAE [15] & ∠ADF = ∠ADE [16] (Similar Triangles)⇒  DA:DF = DE:DA [17]
        # 009. DE:DA = DA:DF [17] & DB = DA [01] ⇒  DE:DB = DB:DF [18]
        # 010. D,E,F are collinear [05] & D,A,B are collinear [00] ⇒  ∠FDB = ∠EDB [19]
        # 011. DE:DB = DB:DF [18] & ∠FDB = ∠EDB [19] (Similar Triangles)⇒  ∠DFB = ∠EBD [20]
        # 012. D,A,B are collinear [00] & B,G,F are collinear [06] & ∠GFE = ∠GHE [11] & D,E,F are collinear [05] & E,H,B are collinear [09] & ∠DFB = ∠EBD [20] ⇒  ∠(DA-FG) = ∠HGF [21]
        # 013. ∠(DA-FG) = ∠HGF [21] ⇒  DA ∥ GH [22]
        # 014. DA ∥ GH [22] & D,A,B are collinear [00] ⇒  AB ∥ GH
        # p1 = state.check_conditions(Concyclic(Point('g'),Point('f'),Point('e'),Point('h')))
        # p2 = state.check_conditions(Angle(Point('g'),Point('f'),Point('e'))-Angle(Point('g'),Point('h'),Point('e')))
        # p3 = state.check_conditions(Circumcenter(Point('c'),Point('a'),Point('e'),Point('f')))
        # p4 = state.check_conditions(Perpendicular(Point('c'),Point('a'),Point('a'),Point('d')))
        # p5 = state.check_conditions(Angle(Point('d'),Point('a'),Point('e'))+Angle(Point('a'),Point('f'),Point('e'))-pi)
        # p6 = state.check_conditions(Angle(Point('a'),Point('f'),Point('d'))-Angle(Point('d'),Point('a'),Point('e')))
        # p7 = state.check_conditions(Angle(Point('a'),Point('d'),Point('f'))-Angle(Point('a'),Point('d'),Point('e')))
        # p8 = state.check_conditions(Length(Point('d'),Point('a'))/Length(Point('d'),Point('f'))-Length(Point('d'),Point('e'))/Length(Point('d'),Point('a')))
        # p9 = state.check_conditions(Length(Point('d'),Point('e'))/Length(Point('d'),Point('b'))-Length(Point('d'),Point('b'))/Length(Point('d'),Point('f')))
        # p10 = state.check_conditions(Angle(Point('f'),Point('d'),Point('b'))-Angle(Point('e'),Point('d'),Point('b')))
        # p11 = state.check_conditions(Angle(Point('d'),Point('f'),Point('b'))-Angle(Point('e'),Point('b'),Point('d')))
        # p12 = state.check_conditions(Angle(Point('g'),Point('b'),Point('a'))-Angle(Point('h'),Point('g'),Point('f')))
        # p7 = state.check_conditions(Concyclic(Point('b'),Point('q'),Point('p'),Point('c')))
        # print(state.goal)
        # print(state.complete())
        # input()
        
    t = time.time() - t0
    result = state.complete()
    if result is not None:
        print(f"Solved in {t:.2f}s")
        
        if args.show_proof:
            t0 = time.time()
            with TT(600):
                proof_generator.run()
                # proof = proof_generator.format_proof()
                # max_cond_num = 0
                # acc_cond_num = 0
                # step = 0
                proof_generator.show_proof()
                print(f"Proof generated in {time.time()-t0:.2f}s")
            
            # print(f'proof genratation runs in {time.time()-t0}')
            # print(f'Proof steps: ', step)
            # print(f'Max condition number: ', max_cond_num)
            # print(f'Average condition number: ', acc_cond_num / step)
    else:
        print(f"Not solved in {t:.2f}s")

if __name__ == '__main__':
    args = parser.parse_args()
    run_single_problem(args)
