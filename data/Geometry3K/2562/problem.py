import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('A'),Point('B')) - sympy.simplify('3')), (Length(Point('A'),Point('B')) - Variable('radius_A'))]
goal = ((sympy.simplify('pi') * Variable('radius_A')) * Variable('radius_A'))
solution = '28.3'

diagrammatic_relations = set()

new_diagrammatic_relations = set()

