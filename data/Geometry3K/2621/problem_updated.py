import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('R'),Point('T')) - ((sympy.simplify('3') * Variable('x')) + sympy.simplify('3'))), (Length(Point('R'),Point('S')) - ((sympy.simplify('4') * Variable('x')) - sympy.simplify('4'))), (Length(Point('S'),Point('T')) - (sympy.simplify('12') + Variable('x'))), (Length(Point('R'),Point('T')) - Length(Point('R'),Point('S')))]
goal = Length(Point('S'),Point('T'))
solution = '19'

diagrammatic_relations = {NotCollinear(Point('R'),Point('S'),Point('T'))}
