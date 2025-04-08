import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('C'),Point('D')) - Variable('x')), (Length(Point('B'),Point('D')) - sympy.simplify('14')), (Length(Point('B'),Point('C')) - sympy.simplify('10')), Perpendicular(Point('B'),Point('C'),Point('C'),Point('D'))]
goal = Variable('x')
solution = '4*sqrt(6)'

diagrammatic_relations = [SameSide(Point('A'),Point('B'),Point('C'),Point('D')), NotCollinear(Point('A'),Point('C'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('C')), SameSide(Point('A'),Point('D'),Point('B'),Point('C')), NotCollinear(Point('A'),Point('B'),Point('D')), SameSide(Point('C'),Point('D'),Point('A'),Point('B')), OppositeSide(Point('A'),Point('C'),Point('B'),Point('D')), SameSide(Point('B'),Point('C'),Point('A'),Point('D')), NotCollinear(Point('B'),Point('C'),Point('D')), OppositeSide(Point('B'),Point('D'),Point('A'),Point('C'))]
