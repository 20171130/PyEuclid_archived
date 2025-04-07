import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


relations = [(Length(Point('D'),Point('F')) - ((sympy.simplify('8.50000000000000') * Variable('x')) + sympy.simplify('3'))), (Length(Point('E'),Point('F')) - ((sympy.simplify('3.50000000000000') * Variable('x')) + sympy.simplify('4'))), (Length(Point('D'),Point('E')) - (sympy.simplify('10') * Variable('x'))), (Length(Point('D'),Point('F')) - Length(Point('D'),Point('E'))),  (Angle(Point('D'),Point('E'),Point('F')) - Angle(Point('D'),Point('F'),Point('E')))]
goal = Length(Point('E'),Point('F'))
solution = '11'

diagrammatic_relations = {NotCollinear(Point('D'),Point('E'),Point('F'))}
