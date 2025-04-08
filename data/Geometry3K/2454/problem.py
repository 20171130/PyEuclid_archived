import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('A'),Point('B')) - Variable('x')), (Angle(Point('A'),Point('B'),Point('C')) - sympy.simplify('17/180*pi')), (Length(Point('B'),Point('C')) - sympy.simplify('9.70000000000000')), Perpendicular(Point('A'),Point('B'),Point('A'),Point('C'))]
goal = Variable('x')
solution = '9.3'

diagrammatic_relations = [NotCollinear(Point('A'),Point('B'),Point('C'))]
