import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


relations = [(Length(Point('Q'),Point('T')) - ((sympy.simplify('2') * Variable('x')) - sympy.simplify('6'))), (Length(Point('R'),Point('S')) - sympy.simplify('7')), (Length(Point('Q'),Point('R')) - (Variable('x') + sympy.simplify('3'))), (Length(Point('S'),Point('T')) - sympy.simplify('7')), Between(Point('S'),Point('R'),Point('T')), Collinear(Point('R'),Point('S'),Point('T')), Between(Point('Q'),Point('A'),Point('S')), Collinear(Point('A'),Point('Q'),Point('S')), Perpendicular(Point('Q'),Point('S'),Point('S'),Point('T'))]
goal = Length(Point('Q'),Point('T'))
solution = '12'

diagrammatic_relations = {Between(Point('S'),Point('R'),Point('T')), SameSide(Point('A'),Point('Q'),Point('R'),Point('T')), OppositeSide(Point('R'),Point('T'),Point('Q'),Point('S')), NotCollinear(Point('Q'),Point('R'),Point('S')), SameSide(Point('S'),Point('T'),Point('Q'),Point('R')), SameSide(Point('S'),Point('T'),Point('A'),Point('R')), NotCollinear(Point('A'),Point('R'),Point('T')), SameSide(Point('Q'),Point('S'),Point('A'),Point('R')), OppositeSide(Point('A'),Point('R'),Point('Q'),Point('T')), OppositeSide(Point('R'),Point('T'),Point('A'),Point('S')), SameSide(Point('Q'),Point('R'),Point('A'),Point('T')), SameSide(Point('A'),Point('Q'),Point('R'),Point('S')), OppositeSide(Point('A'),Point('S'),Point('Q'),Point('R')), NotCollinear(Point('A'),Point('S'),Point('T')), NotCollinear(Point('A'),Point('Q'),Point('T')), SameSide(Point('A'),Point('Q'),Point('S'),Point('T')), SameSide(Point('R'),Point('S'),Point('A'),Point('T')), SameSide(Point('R'),Point('S'),Point('Q'),Point('T')), NotCollinear(Point('Q'),Point('S'),Point('T')), OppositeSide(Point('R'),Point('T'),Point('A'),Point('Q')), OppositeSide(Point('A'),Point('T'),Point('Q'),Point('R')), SameSide(Point('Q'),Point('S'),Point('A'),Point('T')), OppositeSide(Point('A'),Point('S'),Point('Q'),Point('T')), NotCollinear(Point('Q'),Point('R'),Point('T')), SameSide(Point('Q'),Point('T'),Point('A'),Point('R')), NotCollinear(Point('A'),Point('Q'),Point('R')), NotCollinear(Point('A'),Point('R'),Point('S'))}
