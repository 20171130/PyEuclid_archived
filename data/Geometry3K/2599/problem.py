import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [Between(Point('P'),Point('Q'),Point('S')), Collinear(Point('P'),Point('Q'),Point('S')), Between(Point('T'),Point('R'),Point('S')), Collinear(Point('R'),Point('S'),Point('T')), Parallel(Point('P'),Point('T'),Point('Q'),Point('R')), (Length(Point('S'),Point('T')) - sympy.simplify('8')), (Length(Point('R'),Point('T')) - sympy.simplify('4')), (Length(Point('P'),Point('T')) - sympy.simplify('6')), (Length(Point('S'),Point('T')) - sympy.simplify('8')), (Length(Point('R'),Point('T')) - sympy.simplify('4')), (Length(Point('P'),Point('T')) - sympy.simplify('6'))]
goal = Length(Point('Q'),Point('R'))
solution = '9'

diagrammatic_relations = [OppositeSide(Point('Q'),Point('T'),Point('P'),Point('R')), SameSide(Point('P'),Point('Q'),Point('R'),Point('S')), SameSide(Point('S'),Point('T'),Point('P'),Point('R')), OppositeSide(Point('R'),Point('S'),Point('Q'),Point('T')), OppositeSide(Point('Q'),Point('S'),Point('P'),Point('R')), OppositeSide(Point('P'),Point('R'),Point('Q'),Point('T')), NotCollinear(Point('P'),Point('S'),Point('T')), SameSide(Point('P'),Point('S'),Point('Q'),Point('T')), NotCollinear(Point('P'),Point('R'),Point('S')), SameSide(Point('Q'),Point('R'),Point('P'),Point('T')), NotCollinear(Point('Q'),Point('R'),Point('S')), SameSide(Point('S'),Point('T'),Point('Q'),Point('R')), NotCollinear(Point('P'),Point('Q'),Point('T')), NotCollinear(Point('P'),Point('Q'),Point('R')), SameSide(Point('R'),Point('T'),Point('P'),Point('Q')), OppositeSide(Point('Q'),Point('S'),Point('P'),Point('T')), SameSide(Point('R'),Point('T'),Point('P'),Point('S')), SameSide(Point('P'),Point('Q'),Point('S'),Point('T')), SameSide(Point('P'),Point('S'),Point('Q'),Point('R')), NotCollinear(Point('Q'),Point('S'),Point('T')), SameSide(Point('P'),Point('Q'),Point('R'),Point('T')), NotCollinear(Point('P'),Point('R'),Point('T')), NotCollinear(Point('Q'),Point('R'),Point('T')), SameSide(Point('R'),Point('T'),Point('Q'),Point('S')), OppositeSide(Point('R'),Point('S'),Point('P'),Point('T')), SameSide(Point('P'),Point('T'),Point('Q'),Point('R'))]
