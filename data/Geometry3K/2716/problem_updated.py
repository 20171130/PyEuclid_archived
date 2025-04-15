import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('A'),Point('B')) - sympy.simplify('33')), (Length(Point('A'),Point('C')) - Variable('x')), (Length(Point('B'),Point('C')) - sympy.simplify('66')), Perpendicular(Point('A'),Point('B'),Point('A'),Point('C'))]
goal = Variable('x')
solution = '33*sqrt(3)'

diagrammatic_relations = {NotCollinear(Point('A'),Point('B'),Point('C'))}
