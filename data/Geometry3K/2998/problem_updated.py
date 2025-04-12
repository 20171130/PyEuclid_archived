import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('A'),Point('C')) - Variable('x')), (Angle(Point('A'),Point('C'),Point('B')) - sympy.simplify('60/180*pi')), (Length(Point('B'),Point('C')) - Variable('y')), (Length(Point('A'),Point('B')) - sympy.simplify('14')), Perpendicular(Point('A'),Point('B'),Point('A'),Point('C'))]
goal = Variable('y')
solution = '(28 * sqrt(3))/(3)'

diagrammatic_relations = {NotCollinear(Point('A'),Point('B'),Point('C'))}
