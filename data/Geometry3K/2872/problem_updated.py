import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Angle(Point('C'),Point('A'),Point('D')) - sympy.simplify('142/180*pi')), (Angle(Point('C'),Point('B'),Point('D')) - Variable('angle_1')), (Length(Point('A'),Point('B')) - Variable('radius_A')), (Length(Point('A'),Point('C')) - Variable('radius_A')), (Length(Point('A'),Point('D')) - Variable('radius_A'))]
goal = Variable('angle_1')
solution = '(109)/180*pi'

diagrammatic_relations = {SameSide(Point('B'),Point('D'),Point('A'),Point('C')), SameSide(Point('B'),Point('C'),Point('A'),Point('D')), NotCollinear(Point('B'),Point('C'),Point('D')), OppositeSide(Point('C'),Point('D'),Point('A'),Point('B')), OppositeSide(Point('A'),Point('B'),Point('C'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('C')), SameSide(Point('A'),Point('C'),Point('B'),Point('D')), SameSide(Point('A'),Point('D'),Point('B'),Point('C')), NotCollinear(Point('A'),Point('C'),Point('D'))}
