import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('B'),Point('C')) - Variable('x')), (Angle(Point('B'),Point('A'),Point('C')) - sympy.simplify('45/180*pi')), (Length(Point('A'),Point('B')) - Variable('y')), (Length(Point('A'),Point('C')) - sympy.simplify('12')), Perpendicular(Point('A'),Point('B'),Point('B'),Point('C'))]
goal = Variable('y')
solution = '6*sqrt(2)'

diagrammatic_relations = {NotCollinear(Point('A'),Point('B'),Point('C'))}
