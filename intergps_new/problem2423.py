import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


relations = [(Length(Point('A'),Point('C')) - (Variable('x') - sympy.simplify('3'))), (Length(Point('B'),Point('C')) - ((sympy.simplify('4') * Variable('x')) - sympy.simplify('21'))), (Length(Point('A'),Point('B')) - ((sympy.simplify('2') * Variable('x')) - sympy.simplify('7'))), (Length(Point('A'),Point('B')) - Length(Point('B'),Point('C'))), (Length(Point('A'),Point('B')) - Length(Point('B'),Point('C'))), (Length(Point('A'),Point('B')) - Length(Point('B'),Point('C'))), (Length(Point('A'),Point('B')) - Length(Point('B'),Point('C')))]
goal = Length(Point('A'),Point('B'))
solution = '7'

diagrammatic_relations = {NotCollinear(Point('A'),Point('B'),Point('C'))}
