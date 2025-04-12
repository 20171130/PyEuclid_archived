import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('R'),Point('S')) - sympy.simplify('37')), (Length(Point('Q'),Point('R')) - sympy.simplify('18')), (Length(Point('Q'),Point('S')) - sympy.simplify('23'))]
goal = Angle(Point('Q'),Point('R'),Point('S'))
solution = '(29.1)/180*pi'

diagrammatic_relations = {NotCollinear(Point('Q'),Point('R'),Point('S'))}
