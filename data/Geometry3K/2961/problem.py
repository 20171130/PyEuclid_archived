import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('K'),Point('L')) - ((sympy.simplify('11') * Variable('x')) - sympy.simplify('8'))), (Length(Point('J'),Point('L')) - (Variable('x') + sympy.simplify('12'))), (Length(Point('J'),Point('K')) - (sympy.simplify('7') * Variable('x'))), (Length(Point('K'),Point('L')) - Length(Point('J'),Point('K'))), (Length(Point('J'),Point('K')) - Length(Point('J'),Point('L')))]
goal = Length(Point('J'),Point('L'))
solution = '14'

diagrammatic_relations = [NotCollinear(Point('J'),Point('K'),Point('L'))]
