import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('R'),Point('S')) - ((sympy.simplify('6') * Variable('x')) - sympy.simplify('5'))), (Length(Point('Q'),Point('R')) - (sympy.simplify('5') * Variable('x'))), (Length(Point('Q'),Point('S')) - ((sympy.simplify('3') * Variable('x')) + sympy.simplify('10'))), (Length(Point('R'),Point('S')) - Length(Point('Q'),Point('R'))), (Length(Point('Q'),Point('R')) - Length(Point('Q'),Point('S')))]
goal = Length(Point('Q'),Point('S'))
solution = '25'

diagrammatic_relations = [NotCollinear(Point('Q'),Point('R'),Point('S'))]
