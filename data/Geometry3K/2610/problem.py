import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Angle(Point('B'),Point('A'),Point('C')) - sympy.simplify('60/180*pi')), (Length(Point('A'),Point('C')) - Variable('y')), (Length(Point('A'),Point('B')) - sympy.simplify('12')), (Length(Point('B'),Point('C')) - Variable('x')), Perpendicular(Point('A'),Point('C'),Point('B'),Point('C'))]
goal = Variable('y')
solution = '6'

diagrammatic_relations = [NotCollinear(Point('A'),Point('B'),Point('C'))]
