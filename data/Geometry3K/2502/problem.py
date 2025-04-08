import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Angle(Point('A'),Point('B'),Point('C')) - Variable('angle_4')), (Angle(Point('B'),Point('A'),Point('D')) - sympy.simplify('123/180*pi')), Between(Point('A'),Point('C'),Point('D')), Collinear(Point('A'),Point('C'),Point('D')), Perpendicular(Point('B'),Point('C'),Point('C'),Point('D'))]
goal = Variable('angle_4')
solution = '(33)/180*pi'

diagrammatic_relations = [NotCollinear(Point('A'),Point('B'),Point('C')), SameSide(Point('A'),Point('D'),Point('B'),Point('C')), NotCollinear(Point('A'),Point('B'),Point('D')), OppositeSide(Point('C'),Point('D'),Point('A'),Point('B')), SameSide(Point('A'),Point('C'),Point('B'),Point('D')), NotCollinear(Point('B'),Point('C'),Point('D'))]
