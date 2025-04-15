import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Angle(Point('B'),Point('A'),Point('D')) - sympy.simplify('47/180*pi')), (Angle(Point('B'),Point('C'),Point('D')) - sympy.simplify('55/180*pi')), (Length(Point('C'),Point('D')) - sympy.simplify('12')), (Length(Point('B'),Point('D')) - Variable('x')), (Length(Point('A'),Point('B')) - Variable('y')), Between(Point('D'),Point('A'),Point('C')), Collinear(Point('A'),Point('C'),Point('D')), Perpendicular(Point('A'),Point('D'),Point('B'),Point('D'))]
goal = Variable('y')
solution = '23.4'

diagrammatic_relations = {SameSide(Point('C'),Point('D'),Point('A'),Point('B')), NotCollinear(Point('B'),Point('C'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('D')), OppositeSide(Point('A'),Point('C'),Point('B'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('C')), SameSide(Point('A'),Point('D'),Point('B'),Point('C')), Between(Point('D'),Point('A'),Point('C'))}
