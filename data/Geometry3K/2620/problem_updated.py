import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('A'),Point('C')) - Variable('x')), (Length(Point('A'),Point('B')) - sympy.simplify('15')), (Angle(Point('A'),Point('C'),Point('B')) - sympy.simplify('60/180*pi')), (Length(Point('B'),Point('C')) - Variable('y')), Perpendicular(Point('A'),Point('B'),Point('A'),Point('C'))]
goal = Variable('x')
solution = '5*sqrt(3)'

diagrammatic_relations = {NotCollinear(Point('A'),Point('B'),Point('C'))}
