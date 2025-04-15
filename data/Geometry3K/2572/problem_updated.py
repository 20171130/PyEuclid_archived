import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Angle(Point('N'),Point('M'),Point('P')) - sympy.simplify('56/180*pi')), (Angle(Point('M'),Point('N'),Point('Q')) - sympy.simplify('45/180*pi')), Between(Point('P'),Point('N'),Point('Q')), Collinear(Point('N'),Point('P'),Point('Q'))]
goal = Angle(Point('M'),Point('P'),Point('Q'))
solution = '(101)/180*pi'

diagrammatic_relations = {OppositeSide(Point('N'),Point('Q'),Point('M'),Point('P')), SameSide(Point('N'),Point('P'),Point('M'),Point('Q')), NotCollinear(Point('M'),Point('N'),Point('Q')), NotCollinear(Point('M'),Point('P'),Point('Q')), SameSide(Point('P'),Point('Q'),Point('M'),Point('N')), Between(Point('P'),Point('N'),Point('Q')), NotCollinear(Point('M'),Point('N'),Point('P'))}
