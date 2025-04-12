import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('D'),Point('E')) - (Variable('x') - sympy.simplify('4'))), (Length(Point('A'),Point('B')) - Variable('x')), (Length(Point('E'),Point('F')) - sympy.simplify('3')), (Length(Point('B'),Point('C')) - sympy.simplify('5')), (Angle(Point('B'),Point('A'),Point('C')) - Angle(Point('E'),Point('D'),Point('F'))), (Angle(Point('A'),Point('B'),Point('C')) - Angle(Point('D'),Point('E'),Point('F')))]
goal = Length(Point('A'),Point('B'))
solution = '10'

diagrammatic_relations = {NotCollinear(Point('A'),Point('B'),Point('C'))}
