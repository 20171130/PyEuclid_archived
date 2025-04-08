import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('A'),Point('D')) - sympy.simplify('4')), (Length(Point('B'),Point('E')) - sympy.simplify('12')), (Length(Point('C'),Point('E')) - sympy.simplify('5')), (Length(Point('A'),Point('B')) - Variable('x')), Between(Point('A'),Point('B'),Point('D')), Collinear(Point('A'),Point('B'),Point('D')), Between(Point('E'),Point('B'),Point('C')), Collinear(Point('B'),Point('C'),Point('E')), Parallel(Point('A'),Point('E'),Point('C'),Point('D'))]
goal = Variable('x')
solution = '9.6'

diagrammatic_relations = [NotCollinear(Point('A'),Point('B'),Point('E')), SameSide(Point('A'),Point('B'),Point('D'),Point('E')), SameSide(Point('A'),Point('E'),Point('C'),Point('D')), OppositeSide(Point('B'),Point('D'),Point('A'),Point('E')), SameSide(Point('A'),Point('D'),Point('C'),Point('E')), SameSide(Point('A'),Point('B'),Point('C'),Point('D')), SameSide(Point('A'),Point('D'),Point('B'),Point('C')), SameSide(Point('C'),Point('E'),Point('A'),Point('B')), NotCollinear(Point('A'),Point('C'),Point('E')), OppositeSide(Point('A'),Point('C'),Point('D'),Point('E')), OppositeSide(Point('B'),Point('C'),Point('A'),Point('E')), SameSide(Point('A'),Point('D'),Point('B'),Point('E')), SameSide(Point('B'),Point('E'),Point('C'),Point('D')), OppositeSide(Point('B'),Point('D'),Point('A'),Point('C')), SameSide(Point('C'),Point('D'),Point('A'),Point('E')), SameSide(Point('C'),Point('E'),Point('B'),Point('D')), NotCollinear(Point('C'),Point('D'),Point('E')), SameSide(Point('B'),Point('E'),Point('A'),Point('C')), NotCollinear(Point('A'),Point('C'),Point('D')), SameSide(Point('C'),Point('E'),Point('A'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('C')), NotCollinear(Point('A'),Point('D'),Point('E')), OppositeSide(Point('B'),Point('C'),Point('D'),Point('E')), NotCollinear(Point('B'),Point('D'),Point('E')), NotCollinear(Point('B'),Point('C'),Point('D')), OppositeSide(Point('D'),Point('E'),Point('A'),Point('C'))]
