import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('C'),Point('D')) - Variable('x')), (Length(Point('A'),Point('C')) - Variable('y')), (Length(Point('B'),Point('D')) - sympy.simplify('12.5000000000000')), (Length(Point('A'),Point('D')) - sympy.simplify('8')), (Length(Point('B'),Point('C')) - Variable('z')), Between(Point('D'),Point('A'),Point('B')), Collinear(Point('A'),Point('B'),Point('D')), Perpendicular(Point('A'),Point('C'),Point('B'),Point('C')), Perpendicular(Point('B'),Point('D'),Point('C'),Point('D'))]
goal = Variable('y')
solution = '2*sqrt(41)'

diagrammatic_relations = {Between(Point('D'),Point('A'),Point('B')), SameSide(Point('B'),Point('D'),Point('A'),Point('C')), NotCollinear(Point('B'),Point('C'),Point('D')), OppositeSide(Point('A'),Point('B'),Point('C'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('C')), SameSide(Point('A'),Point('D'),Point('B'),Point('C')), NotCollinear(Point('A'),Point('C'),Point('D'))}
