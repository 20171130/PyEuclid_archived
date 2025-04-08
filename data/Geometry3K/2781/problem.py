import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Angle(Point('B'),Point('A'),Point('E')) - Variable('angle_1')), Between(Point('E'),Point('B'),Point('D')), Collinear(Point('B'),Point('D'),Point('E')), Between(Point('E'),Point('A'),Point('C')), Collinear(Point('A'),Point('C'),Point('E')), Rhombus(Point('A'),Point('B'),Point('C'),Point('D')), (Angle(Point('A'),Point('B'),Point('C')) - sympy.simplify('70/180*pi')), Rhombus(Point('A'),Point('B'),Point('C'),Point('D')), (Angle(Point('A'),Point('B'),Point('C')) - sympy.simplify('70/180*pi'))]
goal = Variable('angle_1')
solution = '(55)/180*pi'

diagrammatic_relations = [NotCollinear(Point('A'),Point('B'),Point('E')), OppositeSide(Point('A'),Point('C'),Point('B'),Point('E')), SameSide(Point('C'),Point('D'),Point('A'),Point('B')), SameSide(Point('A'),Point('E'),Point('C'),Point('D')), SameSide(Point('B'),Point('E'),Point('A'),Point('D')), OppositeSide(Point('B'),Point('D'),Point('A'),Point('E')), SameSide(Point('A'),Point('B'),Point('C'),Point('D')), SameSide(Point('D'),Point('E'),Point('A'),Point('B')), SameSide(Point('A'),Point('D'),Point('B'),Point('C')), SameSide(Point('C'),Point('E'),Point('A'),Point('B')), OppositeSide(Point('A'),Point('C'),Point('D'),Point('E')), SameSide(Point('B'),Point('E'),Point('C'),Point('D')), SameSide(Point('A'),Point('E'),Point('B'),Point('C')), SameSide(Point('D'),Point('E'),Point('B'),Point('C')), OppositeSide(Point('B'),Point('D'),Point('A'),Point('C')), NotCollinear(Point('A'),Point('B'),Point('D')), OppositeSide(Point('A'),Point('C'),Point('B'),Point('D')), NotCollinear(Point('B'),Point('C'),Point('E')), NotCollinear(Point('C'),Point('D'),Point('E')), SameSide(Point('B'),Point('C'),Point('A'),Point('D')), NotCollinear(Point('A'),Point('C'),Point('D')), SameSide(Point('C'),Point('E'),Point('A'),Point('D')), OppositeSide(Point('B'),Point('D'),Point('C'),Point('E')), NotCollinear(Point('A'),Point('B'),Point('C')), NotCollinear(Point('A'),Point('D'),Point('E')), NotCollinear(Point('B'),Point('C'),Point('D'))]
