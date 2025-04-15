import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('Q'),Point('R')) - (sympy.simplify('4') * Variable('x'))), (Length(Point('R'),Point('S')) - ((sympy.simplify('2') * Variable('x')) + sympy.simplify('1'))), (Length(Point('Q'),Point('S')) - ((sympy.simplify('6') * Variable('x')) - sympy.simplify('1'))), (Length(Point('Q'),Point('R')) - Length(Point('R'),Point('S'))), (Length(Point('R'),Point('S')) - Length(Point('Q'),Point('S'))), (Length(Point('Q'),Point('S')) - Length(Point('Q'),Point('R'))), (Length(Point('Q'),Point('R')) - Length(Point('R'),Point('S'))), (Length(Point('R'),Point('S')) - Length(Point('Q'),Point('S'))), (Length(Point('Q'),Point('S')) - Length(Point('Q'),Point('R')))]
goal = Length(Point('R'),Point('S'))
solution = '2'

diagrammatic_relations = [NotCollinear(Point('Q'),Point('R'),Point('S'))]

new_diagrammatic_relations = {NotCollinear(Point('Q'),Point('R'),Point('S'))}

