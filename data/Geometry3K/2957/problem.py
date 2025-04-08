import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('A'),Point('C')) - Variable('x')), (Length(Point('B'),Point('E')) - sympy.simplify('18')), (Length(Point('A'),Point('D')) - sympy.simplify('10')), (Length(Point('D'),Point('E')) - sympy.simplify('8')), Between(Point('A'),Point('C'),Point('D')), Collinear(Point('A'),Point('C'),Point('D')), Between(Point('E'),Point('B'),Point('D')), Collinear(Point('B'),Point('D'),Point('E')), Perpendicular(Point('A'),Point('E'),Point('D'),Point('E')), Perpendicular(Point('B'),Point('C'),Point('B'),Point('D'))]
goal = Variable('x')
solution = '22.5'

diagrammatic_relations = [SameSide(Point('A'),Point('C'),Point('D'),Point('E')), NotCollinear(Point('A'),Point('B'),Point('E')), SameSide(Point('A'),Point('C'),Point('B'),Point('D')), SameSide(Point('B'),Point('E'),Point('A'),Point('D')), SameSide(Point('B'),Point('C'),Point('A'),Point('E')), OppositeSide(Point('B'),Point('D'),Point('A'),Point('E')), SameSide(Point('A'),Point('D'),Point('C'),Point('E')), SameSide(Point('D'),Point('E'),Point('A'),Point('B')), SameSide(Point('A'),Point('D'),Point('B'),Point('C')), NotCollinear(Point('A'),Point('C'),Point('E')), OppositeSide(Point('C'),Point('D'),Point('A'),Point('B')), SameSide(Point('B'),Point('E'),Point('C'),Point('D')), SameSide(Point('D'),Point('E'),Point('B'),Point('C')), SameSide(Point('A'),Point('E'),Point('B'),Point('C')), SameSide(Point('A'),Point('C'),Point('B'),Point('E')), NotCollinear(Point('A'),Point('B'),Point('D')), OppositeSide(Point('C'),Point('E'),Point('A'),Point('B')), NotCollinear(Point('B'),Point('C'),Point('E')), NotCollinear(Point('C'),Point('D'),Point('E')), SameSide(Point('B'),Point('E'),Point('A'),Point('C')), OppositeSide(Point('C'),Point('D'),Point('A'),Point('E')), OppositeSide(Point('A'),Point('B'),Point('C'),Point('E')), OppositeSide(Point('B'),Point('D'),Point('C'),Point('E')), NotCollinear(Point('A'),Point('B'),Point('C')), NotCollinear(Point('A'),Point('D'),Point('E')), NotCollinear(Point('B'),Point('C'),Point('D'))]
