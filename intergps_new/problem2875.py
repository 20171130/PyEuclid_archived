import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


relations = [(Length(Point('P'),Point('Q')) - sympy.simplify('9')), (Length(Point('Q'),Point('R')) - sympy.simplify('7')), (Length(Point('R'),Point('S')) - sympy.simplify('7')), Between(Point('R'),Point('Q'),Point('S')), Collinear(Point('Q'),Point('R'),Point('S')), Between(Point('P'),Point('A'),Point('R')), Collinear(Point('A'),Point('P'),Point('R')), Perpendicular(Point('P'),Point('R'),Point('Q'),Point('R'))]
goal = Length(Point('P'),Point('S'))
solution = '9'

diagrammatic_relations = {SameSide(Point('A'),Point('P'),Point('Q'),Point('R')), OppositeSide(Point('A'),Point('R'),Point('P'),Point('S')), SameSide(Point('Q'),Point('R'),Point('A'),Point('S')), OppositeSide(Point('Q'),Point('S'),Point('P'),Point('R')), SameSide(Point('A'),Point('P'),Point('R'),Point('S')), NotCollinear(Point('A'),Point('P'),Point('S')), SameSide(Point('A'),Point('P'),Point('Q'),Point('S')), NotCollinear(Point('P'),Point('R'),Point('S')), OppositeSide(Point('A'),Point('Q'),Point('P'),Point('S')), SameSide(Point('P'),Point('Q'),Point('A'),Point('S')), OppositeSide(Point('A'),Point('S'),Point('P'),Point('Q')), SameSide(Point('R'),Point('S'),Point('P'),Point('Q')), NotCollinear(Point('P'),Point('Q'),Point('S')), OppositeSide(Point('Q'),Point('S'),Point('A'),Point('P')), NotCollinear(Point('A'),Point('Q'),Point('S')), SameSide(Point('P'),Point('S'),Point('A'),Point('Q')), SameSide(Point('P'),Point('R'),Point('A'),Point('S')), NotCollinear(Point('P'),Point('Q'),Point('R')), SameSide(Point('Q'),Point('R'),Point('P'),Point('S')), SameSide(Point('R'),Point('S'),Point('A'),Point('Q')), OppositeSide(Point('Q'),Point('S'),Point('A'),Point('R')), SameSide(Point('P'),Point('R'),Point('A'),Point('Q')), NotCollinear(Point('A'),Point('Q'),Point('R')), NotCollinear(Point('A'),Point('P'),Point('Q')), NotCollinear(Point('A'),Point('R'),Point('S')), OppositeSide(Point('A'),Point('R'),Point('P'),Point('Q'))}
