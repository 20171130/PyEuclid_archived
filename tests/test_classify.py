import unittest
from pyeuclid.formalization.relation import Point, Length, Angle, Lt, Collinear, Not
from pyeuclid.formalization.state import State
from pyeuclid.engine.algebraic_system import AlgebraicSystem 
from pyeuclid.engine.deductive_database import DeductiveDatabase
from pyeuclid.engine.inference_rule import InferenceRule, inference_rule_sets
from pyeuclid.engine.proof_generator import ProofGenerator
from pyeuclid.engine.engine import Engine
import sympy
from pyeuclid.formalization.utils import classify_equations, Traced


class Test(unittest.TestCase):
    def test(self):
        equations = ["Angle_A_B_C - Angle_A_C_B", "Angle_A_B_C - pi", "cos(Angle_A_B_C)-1", "Angle_A_B_C - Angle_A_B_D - Angle_D_B_C", "cos(Angle_A_B_C)*Length_B_A-Length_B_C", "Length_A_B-Length_B_C", "Length_A_B-Length_A_M-Length_B_M", "Length_A_B/Length_B_C-Length_D_B/Length_D_C", "Length_A_B/Length_B_C-2", "Length_A_B*Length_A_B-2"]
        equations = [Traced(sympy.sympify(item)) for item in equations]
        
        angle_linear, length_linear, length_ratio, others = classify_equations(equations, {})
        assert set(equations) == set(angle_linear+length_linear+length_ratio+others)
        print(angle_linear)
        print(length_linear)
        print(length_ratio)
        print(others)
        
        
if __name__=="__main__":
    unittest.main()