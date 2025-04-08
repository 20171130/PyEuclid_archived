import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('C'),Point('Q')) - sympy.simplify('5')), (Length(Point('C'),Point('Qprime')) - sympy.simplify('15')), Between(Point('Q'),Point('C'),Point('Qprime')), Collinear(Point('C'),Point('Q'),Point('Qprime')), Between(Point('F'),Point('B'),Point('C')), Collinear(Point('B'),Point('C'),Point('F'))]
goal = (Length(Point('C'),Point('Q')) / Length(Point('C'),Point('Qprime')))
solution = '1/3'

diagrammatic_relations = [SameSide(Point('B'),Point('X'),Point('A'),Point('D')), NotCollinear(Point('A'),Point('D'),Point('X')), OppositeSide(Point('B'),Point('D'),Point('A'),Point('X')), OppositeSide(Point('A'),Point('X'),Point('B'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('X')), SameSide(Point('A'),Point('B'),Point('D'),Point('X')), NotCollinear(Point('B'),Point('D'),Point('X')), SameSide(Point('D'),Point('X'),Point('A'),Point('B')), SameSide(Point('A'),Point('D'),Point('B'),Point('X'))]
