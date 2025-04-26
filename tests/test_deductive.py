import unittest
from pyeuclid.formalization.relation import Point, Length, Angle, Lt
from pyeuclid.formalization.state import State
from pyeuclid.engine.algebraic_system import AlgebraicSystem 
from pyeuclid.engine.deductive_database import DeductiveDatabase
from pyeuclid.engine.inference_rule import InferenceRule
import sympy

a, b, c, d, e, f, g, h = Point("a"), Point("b"), Point("c"), Point("d"), Point("e"), Point("f"), Point("g"), Point("h")


def assert_len(result, target):
    assert len(result) == target, f"Length {len(result)}, which should be {target}"

class Test(unittest.TestCase):
    def test_eqlength(self):
        state = State()
        state.add_point(a, b, c, d, e, f, g, h)
        db = DeductiveDatabase(state)
        solver = AlgebraicSystem(state)
        state.add_equation(Length(a, b)- Length(a, c))
        state.add_equation(1- Length(b, c))
        solver.solve_equation()
        solver.compute_ratio_and_angle_sum()
        class theorem(InferenceRule):
            def __init__(self, a, b, c, d):
                self.a = a
                self.b = b
                self.c = c
                self.d = d
            def condition(self):
                return Length(self.a, self.b) - Length(self.c, self.d), Lt(self.a, self.b), Lt(self.c, self.d)
        results = db.get_applicable_theorems([theorem])
        breakpoint()
        assert theorem(a, b, a, c) in results
        
    # def test_eqangle(self):
    #     state = State()
    #     state.add_point(a, b, c, d, e, f, g, h)
    #     db = DeductiveDatabase(state)
    #     solver = AlgebraicSystem(state)
    #     state.add_equation(Angle(a, b, c)-Angle(a, c, b))
    #     state.add_equation(Angle(a, b, c)-Angle(c, a, b))
    #     solver.solve_equation()
    #     solver.compute_ratio_and_angle_sum()
    #     class theorem(InferenceRule):
    #         def __init__(self, a, b, c, d, e, f):
    #             self.a = a
    #             self.b = b
    #             self.c = c
    #             self.d = d
    #             self.e = e
    #             self.f = f
    #         def condition(self):
    #             return Angle(self.a, self.b, self.c) - Angle(self.d, self.e, self.f),
    #     results = db.get_applicable_theorems([theorem])
    #     assert theorem(a, c, b, c, a, b) in results

    # def test_eqratio(self):
    #     state = State()
    #     state.add_point(a, b, c, d, e, f, g, h)
    #     db = DeductiveDatabase(state)
    #     solver = AlgebraicSystem(state)
    #     state.add_equation(Length(a,b)/Length(c, d)-Length(e, f)/Length(g, h))
    #     solver.solve_equation()
    #     solver.compute_ratio_and_angle_sum()
    #     class theorem(InferenceRule):
    #         def __init__(self, a, b, c, d, e, f, g, h):
    #             self.a = a
    #             self.b = b
    #             self.c = c
    #             self.d = d
    #             self.e = e
    #             self.f = f
    #             self.g = g
    #             self.h = h
    #         def condition(self):
    #             return Length(a, b)/Length(c, d) - Length(e, f)/Length(g, h),
    #     results = db.get_applicable_theorems([theorem])
    #     assert theorem(a, b, c, d, e, f, g, h) in results
        
    # def test_angle_const(self):
    #     state = State()
    #     state.add_equation(Angle(a, b, c) - Angle(a, c, b))
    #     state.add_equation(Angle(a, b, c) - sympy.pi)
    #     state.add_equation(Angle(c, a, b) - 1)
    #     solver = AlgebraicSystem(state)
    #     solver.solve_equation()
    #     db = DeductiveDatabase(state)
    #     db.insert_points(a, b, c, d)
    #     db.update_equivalence_class(state.angles.equivalence_classes().values(), "angle")
    #     class theorem(InferenceRule):
    #         def __init__(self, a, b, c):
    #             self.a = a
    #             self.b = b
    #             self.c = c
    #         def condition(self):
    #             return Angle(self.a, self.b, self.c) - sympy.pi,
    #     results = db.get_applicable_theorems([theorem])
    #     assert theorem(a, b, c) in results
        
    # def test_angle_sum(self):
    #     state = State()
    #     state.add_equation(Angle(a, b, c) - Angle(a, c, b))
    #     state.add_equation(Angle(a, b, c) - sympy.pi/2)
    #     state.add_equation(Angle(c, a, b) - 1)
    #     solver = AlgebraicSystem(state)
    #     solver.solve_equation()
    #     solver.compute_ratio_and_angle_sum()
    #     db = DeductiveDatabase(state)
    #     db.insert_points(a, b, c, d, e, f)
    #     db.update_equivalence_class(state.angles.equivalence_classes().values(), "angle")
    #     db.update_equivalence_class(state.angle_sums.values(), "angle_sum")
    #     class theorem(InferenceRule):
    #         def __init__(self, a, b, c, d, e, f):
    #             self.a = a
    #             self.b = b
    #             self.c = c
    #             self.d = d
    #             self.e = e
    #             self.f = f
    #         def condition(self):
    #             return Angle(self.a, self.b, self.c) + Angle(self.d, self.e, self.f) - sympy.pi,
    #     results = db.get_applicable_theorems([theorem])
    #     assert theorem(a, b, c, a, c, b) in results
    
if __name__=="__main__":
    unittest.main()