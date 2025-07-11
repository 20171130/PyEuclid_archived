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
# A,B,C = construct_r_triangle(), D = construct_intersection_cc(B,C,A), E = construct_incenter(B,D,A)
parser.add_argument('--problem-id', type=int, help="Problem id from InterGPS dataset, refer to data/Geometry3K for examples.", default=2455)
parser.add_argument('--problem-string', type=str, help="A problem string in jgex format, refer to data/JGEX-AG-231.txt for examples.", default="a b c = r_triangle a b c; d = intersection_cc d b c a; e = incenter e b d a ? eqratio d e a e c e a c")   
parser.add_argument('--show-proof', action='store_true')

def run_single_problem(args):
    state = State()
    # state.silent = True
    state.logger.setLevel(logging.INFO)
    if args.problem_string is not None:
        state.load_problem_from_text(args.problem_string, f'diagrams/JGEX-AG-231/test.jpg')
        state.diagram.draw_diagram()
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
    deductive_database = DeductiveDatabase(state)
    algebraic_system = AlgebraicSystem(state)
    proof_generator = ProofGenerator(state)
    engine = Engine(state, deductive_database, algebraic_system)
    t0 = time.time()
    engine.run()
    # while True:
    #     engine.search(depth=1)

    # 001. DA = DB [03] ⇒  ∠DBA = ∠BAD [07]
    # 002. DB = DC [04] ⇒  ∠DBC = ∠BCD [08]
    # 003. DB = DC [04] & DA = DB [03] ⇒  DA = DC [09]
    # 004. DA = DC [09] ⇒  ∠DAC = ∠ACD [10]
    # 005. GE = GF [05] & GA = GE [06] ⇒  GA = GF [11]
    # 006. GA = GF [11] ⇒  ∠GAF = ∠AFG [12]
    # 007. ∠GAF = ∠AFG [12] & C,A,F are collinear [01] ⇒  ∠GAC = ∠(AC-FG) [13]
    # 008. GA = GE [06] ⇒  ∠GAE = ∠AEG [14]
    # 009. ∠GAE = ∠AEG [14] & B,E,A are collinear [00] ⇒  ∠GAB = ∠(AB-EG) [15]
    # 010. GE = GF [05] ⇒  ∠GFE = ∠FEG [16]
    # 011. ∠GFE = ∠FEG [16] & EF ∥ BC [02] ⇒  ∠(FG-BC) = ∠(BC-EG) [17]
    # 012. ∠DBA = ∠BAD [07] & ∠DBC = ∠BCD [08] & ∠DAC = ∠ACD [10] & ∠GAC = ∠(AC-FG) [13] & ∠GAB = ∠(AB-EG) [15] & ∠(FG-BC) = ∠(BC-EG) [17] (Angle chase)⇒  AD ∥ AG [18]
    # 013. AD ∥ AG [18] ⇒  G,A,D are collinear

    # 1. Angle_b_c_d + Angle_b_d_c + Angle_c_b_d - pi & Angle_a_f_d + Angle_c_f_d - pi & Angle_d_e_g + Angle_d_g_e + Angle_e_d_g - pi => Angle_a_d_b - Angle_a_g_e
    # 2. Angle_b_c_d + Angle_b_d_c + Angle_c_b_d - pi & Angle_a_f_d + Angle_c_f_d - pi & Angle_d_e_g + Angle_d_g_e + Angle_e_d_g - pi => Angle_c_b_d - Angle_f_e_g
    # 3. Angle_c_b_d - Angle_f_e_g & Parallel(b,c,e,f) => Parallel(b,d,e,g)
    # 4. Angle_a_d_b - Angle_a_g_e & Parallel(b,d,e,g) [AlphaGeometry29(a,d,g)] => Collinear(a,d,g)


    # p1 = state.check_conditions(Angle(Point('a'),Point('d'),Point('b'))-Angle(Point('a'),Point('g'),Point('e')))
    # p2 = state.check_conditions(Angle(Point('c'),Point('b'),Point('d'))-Angle(Point('f'),Point('e'),Point('g')))
    # p3 = state.check_conditions(Parallel(Point('b'),Point('d'),Point('e'),Point('g')))
    # print(p1, p2, p3)
    # for cond in AlphaGeometry3a(Point('a'),Point('d'),Point('b'), Point('a'),Point('g'),Point('e')).condition():
    #     print(cond, state.check_conditions(cond))
    # print(state.angles.equivalence_classes())
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
    # print(p1,p2,p3,p4,p5,p6)
        # input()
        
    t = time.time() - t0
    result = state.complete()
    if result is not None:
        print(f"Solved in {t:.2f}s")
        if args.show_proof:
            t0 = time.time()
            proof_generator.run()
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
