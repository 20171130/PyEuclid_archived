import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('A'),Point('B')) - ((sympy.simplify('9') * Variable('x')) - sympy.simplify('1'))), (Length(Point('A'),Point('C')) - ((sympy.simplify('4') * Variable('x')) + sympy.simplify('1'))), (Length(Point('B'),Point('C')) - ((sympy.simplify('5') * Variable('x')) - sympy.simplify('0.500000000000000'))), (Length(Point('A'),Point('C')) - Length(Point('B'),Point('C'))), (Length(Point('A'),Point('B')) - Length(Point('B'),Point('C'))), (Length(Point('A'),Point('B')) - Length(Point('B'),Point('C')))]
goal = Length(Point('A'),Point('C'))
solution = '7'

diagrammatic_relations = [NotCollinear(Point('A'),Point('B'),Point('C'))]

new_diagrammatic_relations = {NotCollinear(Point('A'),Point('B'),Point('C'))}

