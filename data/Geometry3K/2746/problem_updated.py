import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('A'),Point('B')) - ((sympy.simplify('2') * Variable('x')) + sympy.simplify('5'))), (Length(Point('B'),Point('C')) - ((sympy.simplify('3') * Variable('x')) - sympy.simplify('4'))), (Length(Point('A'),Point('C')) - sympy.simplify('27')), (Length(Point('A'),Point('B')) - Length(Point('B'),Point('C')))]
goal = Length(Point('A'),Point('B'))
solution = '23'

diagrammatic_relations = {NotCollinear(Point('A'),Point('B'),Point('C'))}
