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
parser.add_argument('--problem-string', type=str, help="A problem string in jgex format, refer to data/JGEX-AG-231.txt for examples.", default="a b = segment a b; c = on_tline c b a b; d = on_circle d a b; f = midpoint f c b; g = on_line g d f, on_circle g a b; h = intersection_lc h c a g; e = on_line e c d, on_circle e a b ? para b c h e")   
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

        # print(state.angles.equivalence_classes())
        # Solution:
        # 1. Square(a,c,d,e) [PropertyOfSquare(a,c,d,e)] => Rhombus(a,c,d,e)
        # 2. Rhombus(a,c,d,e) [PropertyOfRhombus(a,c,d,e)] => Length_a_c - Length_c_d
        # 3. Square(b,c,f,g) [PropertyOfSquare(b,c,f,g)] => Rhombus(b,c,f,g)
        # 4. Rhombus(b,c,f,g) [PropertyOfRhombus(b,c,f,g)] => Length_b_c - Length_c_f
        # 5. Square(b,c,f,g) [PropertyOfSquare(b,c,f,g)] => Rectangle(b,c,f,g)
        # 6. Rectangle(b,c,f,g) [PropertyOfRectangle(b,c,f,g)] => Angle_b_c_f - pi/2
        # 7. Square(a,c,d,e) [PropertyOfSquare(a,c,d,e)] => Rectangle(a,c,d,e)
        # 8. Rectangle(a,c,d,e) [PropertyOfRectangle(a,c,d,e)] => Angle_a_c_d - pi/2
        # 9. -Angle_a_c_b - Angle_a_c_d + Angle_b_c_d & Angle_b_c_f - pi/2 & -Angle_a_c_b + Angle_a_c_f - Angle_b_c_f & Angle_a_c_d - pi/2 => -Angle_a_c_f + Angle_b_c_d
        # 10. Length_a_c - Length_c_d & -Length_b_c + Length_c_f & Angle_a_c_f - Angle_b_c_d [AlphaGeometry34(a,c,f,d,c,b)] => Congruent3(a,c,f,d,c,b)
        # 11. Congruent3(a,c,f,d,c,b) [PropertyOfCongruent(a,c,f,d,c,b)] => -Angle_b_d_c + Angle_c_a_f
        # 12. Rectangle(a,c,d,e) [PropertyOfRectangle(a,c,d,e)] => -Angle_a_c_e + Angle_c_a_d
        # 13. Rhombus(a,c,d,e) [PropertyOfRhombus(a,c,d,e)] => Perpendicular(a,d,c,e)
        # 14. Perpendicular(a,d,c,e) [Perp2Angle3(a,d,c,e)] => Angle_a_c_e + Angle_c_a_d - pi/2
        # 15. -Angle_a_c_e + Angle_c_a_d & Angle_a_c_e + Angle_c_a_d - pi/2 => Angle_c_a_d - pi/4
        # 16. Perpendicular(a,d,c,e) [Perp2Angle3(a,d,c,e)] => Angle_a_d_c + Angle_d_c_e - pi/2
        # 17. Rectangle(a,c,d,e) [PropertyOfRectangle(a,c,d,e)] => Angle_a_d_c - Angle_d_c_e
        # 18. Angle_a_d_c + Angle_d_c_e - pi/2 & -Angle_a_d_b + Angle_a_d_c - Angle_b_d_c & Angle_a_d_c - Angle_d_c_e => Angle_a_d_b + Angle_b_d_c - pi/4
        # 19. -Angle_c_a_d - Angle_c_a_f + Angle_d_a_f & -Angle_b_d_c + Angle_c_a_f & Angle_c_a_d - pi/4 & Angle_a_d_b + Angle_b_d_c - pi/4 => Angle_a_d_b + Angle_d_a_f - pi/2
        # 20. Angle_a_d_b + Angle_d_a_f - pi/2 [Angle2Perp3(a,f,b,d)] => Perpendicular(a,f,b,d)

    # p1 = state.check_conditions(Angle(Point('a'),Point('c'),Point('f'))-Angle(Point('d'),Point('c'),Point('b')))
    # p2 = state.check_conditions(Congruent3(Point('a'),Point('c'),Point('f'),Point('d'),Point('c'),Point('b')))
    # p3 = state.check_conditions(Angle(Point('a'),Point('d'),Point('b'))+Angle(Point('b'),Point('d'),Point('c'))-pi/4)
    # p4 = state.check_conditions(Angle(Point('a'),Point('d'),Point('b'))+Angle(Point('d'),Point('a'),Point('f'))-pi/2)
    # p5 = state.check_conditions(Angle(Point('c'),Point('a'),Point('d'))-pi/4)
    # p6 = state.check_conditions(Angle(Point('b'),Point('d'),Point('c'))-Angle(Point('c'),Point('a'),Point('f')))
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
