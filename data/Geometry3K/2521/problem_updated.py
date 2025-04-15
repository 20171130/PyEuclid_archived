import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('S'),Point('T')) - (sympy.simplify('2') * Variable('x'))), (Length(Point('R'),Point('T')) - ((sympy.simplify('3') * Variable('x')) - sympy.simplify('9'))), (Length(Point('R'),Point('S')) - (Variable('x') + sympy.simplify('9'))), (Length(Point('R'),Point('S')) - Length(Point('S'),Point('T'))), (Length(Point('S'),Point('T')) - Length(Point('R'),Point('T'))), (Length(Point('R'),Point('T')) - Length(Point('R'),Point('S'))), (Length(Point('R'),Point('S')) - (Variable('x') + sympy.simplify('9'))), (Length(Point('S'),Point('T')) - (sympy.simplify('2') * Variable('x'))), (Length(Point('R'),Point('T')) - ((sympy.simplify('3') * Variable('x')) - sympy.simplify('9'))), (Length(Point('R'),Point('S')) - Length(Point('S'),Point('T'))), (Length(Point('S'),Point('T')) - Length(Point('R'),Point('T'))), (Length(Point('R'),Point('T')) - Length(Point('R'),Point('S'))), (Length(Point('R'),Point('S')) - (Variable('x') + sympy.simplify('9'))), (Length(Point('S'),Point('T')) - (sympy.simplify('2') * Variable('x'))), (Length(Point('R'),Point('T')) - ((sympy.simplify('3') * Variable('x')) - sympy.simplify('9')))]
goal = Variable('x')
solution = '9'

diagrammatic_relations = {NotCollinear(Point('R'),Point('S'),Point('T'))}
