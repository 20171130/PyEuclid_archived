import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [Between(Point('B'),Point('A'),Point('C')), Collinear(Point('A'),Point('B'),Point('C')), Between(Point('E'),Point('A'),Point('D')), Collinear(Point('A'),Point('D'),Point('E')), Parallel(Point('B'),Point('E'),Point('C'),Point('D')), (Length(Point('A'),Point('B')) - sympy.simplify('12')), (Length(Point('A'),Point('C')) - sympy.simplify('16')), (Length(Point('D'),Point('E')) - sympy.simplify('5')), (Length(Point('A'),Point('B')) - sympy.simplify('12')), (Length(Point('A'),Point('C')) - sympy.simplify('16')), (Length(Point('D'),Point('E')) - sympy.simplify('5'))]
goal = Length(Point('A'),Point('E'))
solution = '15'

diagrammatic_relations = [SameSide(Point('C'),Point('D'),Point('B'),Point('E')), NotCollinear(Point('A'),Point('B'),Point('E')), OppositeSide(Point('A'),Point('C'),Point('B'),Point('E')), SameSide(Point('A'),Point('E'),Point('C'),Point('D')), SameSide(Point('B'),Point('C'),Point('A'),Point('E')), SameSide(Point('A'),Point('B'),Point('C'),Point('D')), SameSide(Point('D'),Point('E'),Point('A'),Point('B')), NotCollinear(Point('A'),Point('C'),Point('E')), OppositeSide(Point('A'),Point('D'),Point('B'),Point('E')), OppositeSide(Point('A'),Point('D'),Point('C'),Point('E')), SameSide(Point('B'),Point('E'),Point('C'),Point('D')), SameSide(Point('D'),Point('E'),Point('B'),Point('C')), SameSide(Point('B'),Point('C'),Point('D'),Point('E')), SameSide(Point('A'),Point('B'),Point('C'),Point('E')), SameSide(Point('A'),Point('E'),Point('B'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('D')), OppositeSide(Point('A'),Point('C'),Point('B'),Point('D')), OppositeSide(Point('C'),Point('E'),Point('B'),Point('D')), NotCollinear(Point('B'),Point('C'),Point('E')), NotCollinear(Point('C'),Point('D'),Point('E')), SameSide(Point('B'),Point('C'),Point('A'),Point('D')), SameSide(Point('D'),Point('E'),Point('A'),Point('C')), NotCollinear(Point('A'),Point('C'),Point('D')), OppositeSide(Point('B'),Point('D'),Point('C'),Point('E')), NotCollinear(Point('B'),Point('D'),Point('E')), NotCollinear(Point('B'),Point('C'),Point('D'))]
