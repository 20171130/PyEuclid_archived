import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Angle(Point('D'),Point('B'),Point('A'))-sympy.simplify('pi/4')), (Angle(Point('C'),Point('B'),Point('D')) - Variable('angle_2')), (Angle(Point('B'),Point('C'),Point('D')) - sympy.simplify('70/180*pi')), (Angle(Point('B'),Point('D'),Point('C')) - Variable('angle_1')), (Angle(Point('A'),Point('D'),Point('B')) - Variable('angle_3')), (Angle(Point('B'),Point('A'),Point('D')) - sympy.simplify('40/180*pi')), Between(Point('D'),Point('A'),Point('C')), Collinear(Point('A'),Point('C'),Point('D'))]
goal = Variable('angle_3')
solution = '(95)/180*pi'

diagrammatic_relations = [NotCollinear(Point('A'),Point('B'),Point('C')), Between(Point('D'),Point('A'),Point('C')), SameSide(Point('A'),Point('D'),Point('B'),Point('C')), NotCollinear(Point('A'),Point('B'),Point('D')), SameSide(Point('C'),Point('D'),Point('A'),Point('B')), OppositeSide(Point('A'),Point('C'),Point('B'),Point('D')), NotCollinear(Point('B'),Point('C'),Point('D'))]
