import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('B'),Point('C')) - Variable('y')), (Length(Point('B'),Point('D')) - Variable('x')), (Length(Point('A'),Point('D')) - sympy.simplify('10')), (Length(Point('A'),Point('B')) - sympy.simplify('12')), (Length(Point('C'),Point('D')) - Variable('z')), Between(Point('D'),Point('A'),Point('C')), Collinear(Point('A'),Point('C'),Point('D')), Perpendicular(Point('A'),Point('B'),Point('B'),Point('C')), Perpendicular(Point('A'),Point('D'),Point('B'),Point('D'))]
goal = Variable('x')
solution = '2*sqrt(11)'

diagrammatic_relations = [NotCollinear(Point('A'),Point('B'),Point('C')), Between(Point('D'),Point('A'),Point('C')), SameSide(Point('A'),Point('D'),Point('B'),Point('C')), NotCollinear(Point('A'),Point('B'),Point('D')), SameSide(Point('C'),Point('D'),Point('A'),Point('B')), OppositeSide(Point('A'),Point('C'),Point('B'),Point('D')), NotCollinear(Point('B'),Point('C'),Point('D'))]
