import unittest

from pyeuclid.formalization.diagram import generate_diagram
from pyeuclid.formalization.state import State

class JGEX_AG_231(unittest.TestCase):
    def test_single(self):
        problem = "a b c = triangle a b c; d = foot d a b c; e = midpoint e b a; f = midpoint f c b; g = midpoint g a c; o = circumcenter o e f g ? cyclic d g e f"
        diagram = generate_diagram(problem)
        state = State()
        state = state.formalize(problem, diagram)