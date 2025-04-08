import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Angle(Point('A'),Point('B'),Point('C')) - sympy.simplify('27/180*pi')), (Angle(Point('A'),Point('D'),Point('C')) - Variable('angle_1')), (Angle(Point('B'),Point('A'),Point('D')) - sympy.simplify('52/180*pi')), Between(Point('D'),Point('B'),Point('C')), Collinear(Point('B'),Point('C'),Point('D'))]
goal = Variable('angle_1')
solution = '(79)/180*pi'

diagrammatic_relations = [NotCollinear(Point('A'),Point('C'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('C')), NotCollinear(Point('A'),Point('B'),Point('D')), SameSide(Point('C'),Point('D'),Point('A'),Point('B')), OppositeSide(Point('B'),Point('C'),Point('A'),Point('D')), SameSide(Point('B'),Point('D'),Point('A'),Point('C'))]
