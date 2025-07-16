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
parser.add_argument('--problem-string', type=str, help="A problem string in jgex format, refer to data/JGEX-AG-231.txt for examples.", default="a b = segment a b; d = midpoint d b a; c = on_tline c a a b; e = on_circle e c a; f = on_line f d e, on_circle f c a; g = on_circle g c f, on_line g f b; h = on_line h b e, on_circle h c a ? para a b g h")   
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
    proof_generator.max_equation_length_perstep = 20
    engine = Engine(state, deductive_database, algebraic_system)
    # Length_b_d/Length_d_f - Length_d_e/Length_b_d
    state.goal = Length(Point('b'),Point('d'))/Length(Point('d'),Point('f')) - Length(Point('d'),Point('e'))/Length(Point('b'),Point('d'))
    t0 = time.time()
    engine.run()
    breakpoint()
    # while True:
    #     engine.search(depth=1)
    
        # 1. Collinear(c,d,e) [CollinearParallel(c,d,e)] => Parallel(c,d,d,e) & Angle_c_d_g + Angle_e_d_g - pi & Parallel(c,d,c,e)
        # 2. Perpendicular(a,b,c,d) & Parallel(c,d,d,e) [AlphaGeometry1b(c,d,a,b,d,e)] => Perpendicular(a,b,d,e)
        # 3. Collinear(a,b,d) [CollinearParallel(a,b,d)] => Parallel(a,b,a,d) & Angle_b_a_e + Angle_d_a_e - pi & Parallel(a,b,b,d)
        # 4. Perpendicular(a,b,d,e) & Parallel(a,b,a,d) [AlphaGeometry1b(a,b,d,e,a,d)] => Perpendicular(a,d,d,e)
        # 5. Midpoint(f,a,e) & Perpendicular(a,d,d,e) [AlphaGeometry20(a,d,e,f)] => Length_d_f - Length_e_f & Length_a_f - Length_d_f
        # 6. Perpendicular(a,e,b,c) [Perp2Angle2(e,a,b,c)] => Angle_a_b_c - Angle_b_a_e + pi/2
        # 7. Perpendicular(a,b,c,d) & Parallel(c,d,c,e) [AlphaGeometry1b(c,d,a,b,c,e)] => Perpendicular(a,b,c,e)
        # 8. Perpendicular(a,b,c,e) [Perp2Angle2(b,a,c,e)] => Angle_a_b_c + Angle_b_c_e - pi/2
        # 9. Collinear(c,d,e) & Collinear(b,c,g) [DiagramAngle4a(c,b,e,g,d)] => Angle_b_c_e - Angle_d_c_g
        # 10. Angle_b_a_e + Angle_d_a_e - pi & Angle_a_b_c - Angle_b_a_e + pi/2 & Angle_a_b_c + Angle_b_c_e - pi/2 & Angle_b_c_e - Angle_d_c_g => Angle_d_a_e - Angle_d_c_g
        # 11. Perpendicular(a,b,c,d) & Parallel(a,b,b,d) [AlphaGeometry1b(a,b,c,d,b,d)] => Perpendicular(b,d,c,d)
        # 12. Midpoint(g,b,c) & Perpendicular(b,d,c,d) [AlphaGeometry20(b,d,c,g)] => Length_c_g - Length_d_g
        # 13. Length_c_g - Length_d_g [DefinitionOfIsoscelesTriangle(g,c,d)] => Angle_c_d_g - Angle_d_c_g
        # 14. Angle_c_d_g + Angle_e_d_g - pi & Angle_d_a_e - Angle_d_c_g & Angle_c_d_g - Angle_d_c_g => Angle_d_a_e + Angle_e_d_g - pi
        # 15. Length_d_f - Length_e_f & -Length_a_f + Length_d_f & Angle_d_a_e + Angle_e_d_g - pi [AlphaGeometry17a(f,d,e,a,g)] => Perpendicular(d,f,d,g)

        # 1. Perpendicular(a,e,b,c) & Parallel(b,c,b,g) [AlphaGeometry1b(b,c,a,e,b,g)] => Perpendicular(a,e,b,g)
        # 2. Perpendicular(a,e,b,g) [Perp2Angle2(e,a,b,g)] => -Angle_a_b_g + Angle_b_a_e - pi/2
        # 3. Perpendicular(a,b,c,d) & Parallel(c,d,c,e) [AlphaGeometry1b(c,d,a,b,c,e)] => Perpendicular(a,b,c,e)
        # 4. Perpendicular(a,b,c,e) [Perp2Angle2(b,a,c,e)] => -Angle_a_e_c + Angle_b_a_e - pi/2
        # 5. -Angle_a_b_g + Angle_b_a_e - pi/2 & -Angle_a_e_c + Angle_b_a_e - pi/2 & -Angle_a_e_c + Angle_d_e_f & -Angle_a_b_g + Angle_d_b_g => -Angle_d_b_g + Angle_d_e_f
        # 6. Perpendicular(a,b,c,d) & Parallel(c,d,d,e) [AlphaGeometry1b(c,d,a,b,d,e)] => Perpendicular(a,b,d,e)
        # 7. Perpendicular(a,b,d,e) & Parallel(a,b,a,d) [AlphaGeometry1b(a,b,d,e,a,d)] => Perpendicular(a,d,d,e)
        # 8. Midpoint(f,a,e) & Perpendicular(a,d,d,e) [AlphaGeometry20(a,d,e,f)] => Length_d_f - Length_e_f
        # 9. Length_d_f - Length_e_f [DefinitionOfIsoscelesTriangle(f,d,e)] => -Angle_d_e_f + Angle_e_d_f
        # 10. Perpendicular(a,b,c,d) & Parallel(a,b,b,d) [AlphaGeometry1b(a,b,c,d,b,d)] => Perpendicular(b,d,c,d)
        # 11. Midpoint(g,b,c) & Perpendicular(b,d,c,d) [AlphaGeometry20(b,d,c,g)] => Length_b_g - Length_d_g
        # 12. Length_b_g - Length_d_g [DefinitionOfIsoscelesTriangle(g,b,d)] => -Angle_b_d_g + Angle_d_b_g
        # 13. -Angle_b_d_e - Angle_b_d_g + Angle_e_d_g & -Angle_d_b_g + Angle_d_e_f & -Angle_d_e_f + Angle_e_d_f & -Angle_b_d_g + Angle_d_b_g & -Angle_e_d_f + Angle_e_d_g - Angle_f_d_g => Angle_b_d_e - Angle_f_d_g
        # 14. Perpendicular(b,d,c,d) [Perp2Angle(b,d,c)] => Angle_b_d_c - pi/2
        # 15. Perpendicular(a,b,d,e) & Parallel(a,b,b,d) [AlphaGeometry1b(a,b,d,e,b,d)] => Perpendicular(b,d,d,e)
        # 16. Perpendicular(b,d,d,e) [Perp2Angle(b,d,e)] => Angle_b_d_e - pi/2
        # 17. Angle_b_d_c - pi/2 & Angle_b_d_e - pi/2 => Angle_b_d_c - Angle_b_d_e
        # 18. -Angle_b_d_e - Angle_b_d_g + Angle_e_d_g & -Angle_d_b_g + Angle_d_e_f & -Angle_d_e_f + Angle_e_d_f & Angle_b_d_c - Angle_b_d_e & -Angle_b_d_g + Angle_d_b_g & -Angle_e_d_f + Angle_e_d_g - Angle_f_d_g => Angle_b_d_c - Angle_f_d_g
        # 19. Angle_b_d_c + Angle_b_d_e - pi & Angle_b_d_e - Angle_f_d_g & Angle_b_d_c - Angle_f_d_g => Angle_f_d_g - pi/2
        # 20. Angle_f_d_g - pi/2 [Angle2Perp(f,d,g)] => Perpendicular(d,f,d,g)

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
