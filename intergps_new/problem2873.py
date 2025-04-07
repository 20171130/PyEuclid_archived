import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


relations = [(Length(Point('A'),Point('C')) - sympy.simplify('6')), (Length(Point('A'),Point('B')) - Variable('y')), (Length(Point('B'),Point('C')) - Variable('x')), (Angle(Point('A'),Point('B'),Point('C')) - sympy.simplify('30/180*pi')), Perpendicular(Point('A'),Point('B'),Point('A'),Point('C'))]
goal = Variable('y')
solution = '6*sqrt(3)'

diagrammatic_relations = {NotCollinear(Point('A'),Point('B'),Point('C'))}
