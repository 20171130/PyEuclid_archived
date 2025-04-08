import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [Between(Point('D'),Point('A'),Point('B')), Collinear(Point('A'),Point('B'),Point('D')), Between(Point('E'),Point('A'),Point('C')), Collinear(Point('A'),Point('C'),Point('E')), Parallel(Point('B'),Point('C'),Point('D'),Point('E')), (Length(Point('B'),Point('D')) - sympy.simplify('24')), (Length(Point('A'),Point('E')) - sympy.simplify('3')), (Length(Point('C'),Point('E')) - sympy.simplify('18')), (Length(Point('B'),Point('D')) - sympy.simplify('24')), (Length(Point('A'),Point('E')) - sympy.simplify('3')), (Length(Point('C'),Point('E')) - sympy.simplify('18'))]
goal = Length(Point('A'),Point('D'))
solution = '4'

diagrammatic_relations = [SameSide(Point('B'),Point('D'),Point('C'),Point('E')), NotCollinear(Point('A'),Point('B'),Point('E')), OppositeSide(Point('A'),Point('C'),Point('B'),Point('E')), SameSide(Point('A'),Point('E'),Point('C'),Point('D')), OppositeSide(Point('B'),Point('E'),Point('C'),Point('D')), OppositeSide(Point('A'),Point('B'),Point('C'),Point('D')), SameSide(Point('B'),Point('D'),Point('A'),Point('E')), SameSide(Point('A'),Point('D'),Point('B'),Point('C')), SameSide(Point('C'),Point('E'),Point('A'),Point('B')), OppositeSide(Point('A'),Point('C'),Point('D'),Point('E')), SameSide(Point('A'),Point('D'),Point('B'),Point('E')), SameSide(Point('D'),Point('E'),Point('B'),Point('C')), SameSide(Point('A'),Point('E'),Point('B'),Point('C')), SameSide(Point('B'),Point('C'),Point('D'),Point('E')), SameSide(Point('C'),Point('E'),Point('B'),Point('D')), NotCollinear(Point('B'),Point('C'),Point('E')), NotCollinear(Point('C'),Point('D'),Point('E')), NotCollinear(Point('A'),Point('C'),Point('D')), SameSide(Point('C'),Point('E'),Point('A'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('C')), OppositeSide(Point('C'),Point('D'),Point('B'),Point('E')), NotCollinear(Point('A'),Point('D'),Point('E')), OppositeSide(Point('A'),Point('B'),Point('D'),Point('E')), NotCollinear(Point('B'),Point('D'),Point('E')), NotCollinear(Point('B'),Point('C'),Point('D')), SameSide(Point('B'),Point('D'),Point('A'),Point('C'))]
