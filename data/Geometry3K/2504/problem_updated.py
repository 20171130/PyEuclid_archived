import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('B'),Point('C')) - sympy.simplify('15')), (Length(Point('A'),Point('B')) - Variable('x')), (Angle(Point('A'),Point('B'),Point('C')) - sympy.simplify('70/180*pi')), Perpendicular(Point('A'),Point('C'),Point('B'),Point('C'))]
goal = Variable('x')
solution = '43.86'

diagrammatic_relations = {NotCollinear(Point('A'),Point('B'),Point('C'))}
