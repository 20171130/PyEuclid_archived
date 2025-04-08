import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('A'),Point('B')) - Variable('x')), (Angle(Point('A'),Point('C'),Point('B')) - sympy.simplify('60/180*pi')), (Length(Point('B'),Point('C')) - sympy.simplify('17')), (Length(Point('A'),Point('C')) - Variable('y')), Perpendicular(Point('A'),Point('B'),Point('A'),Point('C'))]
goal = Variable('x')
solution = '(17)/(2)*sqrt(3)'

diagrammatic_relations = [NotCollinear(Point('A'),Point('B'),Point('C'))]
