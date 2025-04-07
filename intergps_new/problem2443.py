import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


relations = [(Angle(Point('R'),Point('Q'),Point('S')) - Variable('angle_2')), (Angle(Point('P'),Point('Q'),Point('S')) - sympy.simplify('51/180*pi')), (Angle(Point('P'),Point('R'),Point('Q')) - sympy.simplify('33/180*pi')), (Angle(Point('Q'),Point('S'),Point('R')) - Variable('angle_1')), Between(Point('S'),Point('P'),Point('R')), Collinear(Point('P'),Point('R'),Point('S')), Perpendicular(Point('P'),Point('Q'),Point('Q'),Point('R'))]
goal = Variable('angle_1')
solution = '(108)/180*pi'

diagrammatic_relations = {NotCollinear(Point('Q'),Point('R'),Point('S')), SameSide(Point('R'),Point('S'),Point('P'),Point('Q')), NotCollinear(Point('P'),Point('Q'),Point('S')), OppositeSide(Point('P'),Point('R'),Point('Q'),Point('S')), SameSide(Point('P'),Point('S'),Point('Q'),Point('R')), NotCollinear(Point('P'),Point('Q'),Point('R'))}
