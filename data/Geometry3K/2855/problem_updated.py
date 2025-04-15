import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Angle(Point('A'),Point('D'),Point('B')) - sympy.simplify('45/180*pi')), (Length(Point('A'),Point('B')) - Variable('y')), (Length(Point('C'),Point('D')) - Variable('x')), (Length(Point('A'),Point('C')) - sympy.simplify('5')), Between(Point('B'),Point('C'),Point('D')), Collinear(Point('B'),Point('C'),Point('D')), Perpendicular(Point('A'),Point('C'),Point('A'),Point('D')), Perpendicular(Point('A'),Point('B'),Point('B'),Point('C'))]
goal = Variable('y')
solution = '(5*sqrt(2))/(2)'

diagrammatic_relations = {SameSide(Point('B'),Point('D'),Point('A'),Point('C')), SameSide(Point('B'),Point('C'),Point('A'),Point('D')), OppositeSide(Point('C'),Point('D'),Point('A'),Point('B')), NotCollinear(Point('A'),Point('B'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('C')), Between(Point('B'),Point('C'),Point('D')), NotCollinear(Point('A'),Point('C'),Point('D'))}
