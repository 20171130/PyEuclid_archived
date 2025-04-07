import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


relations = [(Length(Point('P'),Point('Q')) - sympy.simplify('25')), (Length(Point('R'),Point('T')) - Variable('x')), (Length(Point('R'),Point('S')) - sympy.simplify('10')), (Length(Point('Q'),Point('S')) - sympy.simplify('5')), Between(Point('T'),Point('P'),Point('R')), Collinear(Point('P'),Point('R'),Point('T')), Between(Point('S'),Point('Q'),Point('R')), Collinear(Point('Q'),Point('R'),Point('S')), Perpendicular(Point('R'),Point('S'),Point('R'),Point('T')), Parallel(Point('P'),Point('Q'),Point('S'),Point('T'))]
goal = Length(Point('P'),Point('T'))
solution = '(20)/(3)'

diagrammatic_relations = {OppositeSide(Point('P'),Point('R'),Point('S'),Point('T')), SameSide(Point('Q'),Point('S'),Point('P'),Point('T')), SameSide(Point('P'),Point('T'),Point('Q'),Point('S')), OppositeSide(Point('P'),Point('R'),Point('Q'),Point('T')), NotCollinear(Point('P'),Point('S'),Point('T')), NotCollinear(Point('P'),Point('R'),Point('S')), OppositeSide(Point('Q'),Point('R'),Point('P'),Point('S')), OppositeSide(Point('Q'),Point('T'),Point('P'),Point('S')), SameSide(Point('Q'),Point('S'),Point('P'),Point('R')), SameSide(Point('S'),Point('T'),Point('P'),Point('Q')), OppositeSide(Point('Q'),Point('R'),Point('S'),Point('T')), SameSide(Point('R'),Point('S'),Point('P'),Point('Q')), NotCollinear(Point('R'),Point('S'),Point('T')), NotCollinear(Point('P'),Point('Q'),Point('S')), NotCollinear(Point('P'),Point('Q'),Point('T')), NotCollinear(Point('P'),Point('Q'),Point('R')), SameSide(Point('Q'),Point('S'),Point('R'),Point('T')), OppositeSide(Point('P'),Point('S'),Point('Q'),Point('T')), SameSide(Point('R'),Point('T'),Point('P'),Point('Q')), SameSide(Point('R'),Point('T'),Point('P'),Point('S')), SameSide(Point('P'),Point('Q'),Point('S'),Point('T')), SameSide(Point('R'),Point('S'),Point('Q'),Point('T')), NotCollinear(Point('Q'),Point('S'),Point('T')), NotCollinear(Point('Q'),Point('R'),Point('T')), SameSide(Point('P'),Point('T'),Point('R'),Point('S')), SameSide(Point('P'),Point('T'),Point('Q'),Point('R'))}
