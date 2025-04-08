import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('Q'),Point('R')) - sympy.simplify('15')), (Length(Point('P'),Point('Q')) - sympy.simplify('17')), (Length(Point('P'),Point('R')) - sympy.simplify('8')), Perpendicular(Point('P'),Point('R'),Point('Q'),Point('R'))]
goal = sympy.cos(Angle(Point('Q'),Point('P'),Point('R')))
solution = '0.47'

diagrammatic_relations = [NotCollinear(Point('P'),Point('Q'),Point('R'))]
