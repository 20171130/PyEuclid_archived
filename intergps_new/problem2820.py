import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


relations = [(Length(Point('A'),Point('B')) - sympy.simplify('4')), (Length(Point('A'),Point('B')) - Variable('radius_A'))]
goal = ((sympy.simplify('pi') * Variable('radius_A')) * Variable('radius_A'))
solution = '50.2'

diagrammatic_relations = set()
