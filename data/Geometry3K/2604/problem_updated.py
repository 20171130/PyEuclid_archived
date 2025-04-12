import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('A'),Point('B')) - Variable('x')), (Length(Point('A'),Point('C')) - (Variable('x') - sympy.simplify('3'))), (Length(Point('B'),Point('C')) - sympy.simplify('9')), Perpendicular(Point('A'),Point('C'),Point('B'),Point('C'))]
goal = Variable('x')
solution = '15'

diagrammatic_relations = {NotCollinear(Point('A'),Point('B'),Point('C'))}
