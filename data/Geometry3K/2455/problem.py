import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('B'),Point('C')) - sympy.simplify('6.20000000000000')), Between(Point('A'),Point('B'),Point('C')), Collinear(Point('A'),Point('B'),Point('C')), (Length(Point('A'),Point('B')) - Variable('radius_A')), (Length(Point('A'),Point('C')) - Variable('radius_A'))]
goal = (sympy.simplify(2 * pi) * Variable('radius_A'))
solution = '19.5'

diagrammatic_relations = set()

new_diagrammatic_relations = {Between(Point('A'),Point('B'),Point('C'))}

