import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


relations = [(Length(Point('B'),Point('C')) - sympy.simplify('4')), (Length(Point('A'),Point('B')) - Variable('x')), (Angle(Point('B'),Point('A'),Point('C')) - sympy.simplify('45/180*pi')), Perpendicular(Point('A'),Point('C'),Point('B'),Point('C'))]
goal = Variable('x')
solution = '4*sqrt(2)'

diagrammatic_relations = {NotCollinear(Point('A'),Point('B'),Point('C'))}
