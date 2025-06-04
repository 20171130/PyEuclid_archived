from pyeuclid.formalization.relation import *
from pyeuclid.formalization.state import State
from pyeuclid.engine.algebraic_system import AlgebraicSystem 
from pyeuclid.engine.deductive_database import DeductiveDatabase
from pyeuclid.engine.inference_rule import InferenceRule, inference_rule_sets
from pyeuclid.engine.engine import Engine
import unittest

a, b, c, d, e, f, g, h = Point("a"), Point("b"), Point("c"), Point("d"), Point("e"), Point("f"), Point("g"), Point("h")

class Test(unittest.TestCase):
    def test_basic(self):
        state = State()
        state.add_relation(Collinear(a, b, c))
        deductive_database = DeductiveDatabase(state, outer_theorems=inference_rule_sets['basic'])
        algebraic_system = AlgebraicSystem(state)
        engine = Engine(state, deductive_database, algebraic_system)
        result = engine.step([Collinear(a, b, c)], [Parallel(a, b, a, c)])
        assert Parallel(a, b, a, c) in result
        
    def test_condition_restriction(self):
        state = State()
        state.add_relation(Collinear(a, b, c))
        state.add_relation(Collinear(d, e, f))
        deductive_database = DeductiveDatabase(state, outer_theorems=inference_rule_sets['basic'])
        algebraic_system = AlgebraicSystem(state)
        engine = Engine(state, deductive_database, algebraic_system)
        result = engine.step([Collinear(d, e, f)], [])
        assert not Parallel(a, b, a, c) in result
        engine.search()
        assert state.check_conditions(Parallel(a, b, a, c))
        
    def test_equation(self):
        state = State()
        state.add_conditions([Length(a, b)-Length(c, d), Length(a, b)-Length(e, f)])
        deductive_database = DeductiveDatabase(state, outer_theorems=inference_rule_sets['basic'])
        algebraic_system = AlgebraicSystem(state)
        engine = Engine(state, deductive_database, algebraic_system)
        result = engine.step([Length(a, b)-Length(c, d), Length(a, b)-Length(e, f)], [])
        assert state.check_conditions(Length(c, d)-Length(e, f))
        
if __name__=="__main__":
    unittest.main()