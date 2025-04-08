import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('X'),Point('Y')) - ((sympy.simplify('4') * Variable('x')) + sympy.simplify('5'))), (Length(Point('W'),Point('Y')) - ((sympy.simplify('6') * Variable('x')) + sympy.simplify('3'))), (Length(Point('W'),Point('X')) - (sympy.simplify('9') * Variable('x'))), (Length(Point('X'),Point('Y')) - Length(Point('W'),Point('Y'))), (Length(Point('W'),Point('Y')) - Length(Point('W'),Point('X')))]
goal = Variable('x')
solution = '1'

diagrammatic_relations = [NotCollinear(Point('W'),Point('X'),Point('Y'))]
