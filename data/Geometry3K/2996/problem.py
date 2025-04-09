import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('P'),Point('S')) - sympy.simplify('3')), (Angle(Point('P'),Point('Q'),Point('R')) - sympy.simplify('128/180*pi')), (Length(Point('R'),Point('S')) - sympy.simplify('5')), Parallelogram(Point('P'),Point('Q'),Point('R'),Point('S')), Parallelogram(Point('P'),Point('Q'),Point('R'),Point('S'))]
goal = Length(Point('P'),Point('Q'))
solution = '5'

diagrammatic_relations = [NotCollinear(Point('Q'),Point('R'),Point('S')), SameSide(Point('P'),Point('Q'),Point('R'),Point('S')), OppositeSide(Point('Q'),Point('S'),Point('P'),Point('R')), SameSide(Point('Q'),Point('R'),Point('P'),Point('S')), SameSide(Point('R'),Point('S'),Point('P'),Point('Q')), NotCollinear(Point('P'),Point('Q'),Point('S')), OppositeSide(Point('P'),Point('R'),Point('Q'),Point('S')), SameSide(Point('P'),Point('S'),Point('Q'),Point('R')), NotCollinear(Point('P'),Point('R'),Point('S')), NotCollinear(Point('P'),Point('Q'),Point('R'))]

new_diagrammatic_relations = {NotCollinear(Point('Q'),Point('R'),Point('S')), OppositeSide(Point('Q'),Point('S'),Point('P'),Point('R')), SameSide(Point('R'),Point('S'),Point('P'),Point('Q')), OppositeSide(Point('P'),Point('R'),Point('Q'),Point('S')), NotCollinear(Point('P'),Point('R'),Point('S')), SameSide(Point('P'),Point('S'),Point('Q'),Point('R')), SameSide(Point('Q'),Point('R'),Point('P'),Point('S')), SameSide(Point('P'),Point('Q'),Point('R'),Point('S')), NotCollinear(Point('P'),Point('Q'),Point('R')), NotCollinear(Point('P'),Point('Q'),Point('S'))}

