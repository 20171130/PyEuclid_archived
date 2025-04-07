import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


relations = [(Length(Point('A'),Point('C')) - sympy.simplify('9')), (Length(Point('A'),Point('B')) - sympy.simplify('15')), (Length(Point('B'),Point('C')) - Variable('x')), Perpendicular(Point('A'),Point('C'),Point('B'),Point('C'))]
goal = Variable('x')
solution = '12'

diagrammatic_relations = {NotCollinear(Point('A'),Point('B'),Point('C'))}
