import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('B'),Point('C')) - Variable('x')), (Length(Point('A'),Point('C')) - Variable('y')), (Angle(Point('A'),Point('B'),Point('C')) - sympy.simplify('60/180*pi')), (Length(Point('A'),Point('B')) - sympy.simplify('18')), Perpendicular(Point('A'),Point('C'),Point('B'),Point('C'))]
goal = Variable('x')
solution = '9'

diagrammatic_relations = {NotCollinear(Point('A'),Point('B'),Point('C'))}
