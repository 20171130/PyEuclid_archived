import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('R'),Point('S')) - (sympy.simplify('4') * sympy.sqrt(sympy.simplify('3')))), (Length(Point('S'),Point('T')) - (sympy.simplify('10') * sympy.sqrt(sympy.simplify('3')))), Perpendicular(Point('R'),Point('S'),Point('S'),Point('T'))]
goal = Angle(Point('R'),Point('T'),Point('S'))
solution = '(21.8)/180*pi'

diagrammatic_relations = [NotCollinear(Point('R'),Point('S'),Point('T'))]
