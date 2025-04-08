import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('A'),Point('B')) - ((sympy.simplify('2') * Variable('x')) + sympy.simplify('11'))), (Length(Point('A'),Point('C')) - ((sympy.simplify('6') * Variable('x')) - sympy.simplify('9'))), (Angle(Point('B'),Point('A'),Point('C')) - Angle(Point('A'),Point('B'),Point('C'))), (Angle(Point('A'),Point('B'),Point('C')) - Angle(Point('A'),Point('C'),Point('B')))]
goal = Variable('x')
solution = '5'

diagrammatic_relations = [NotCollinear(Point('A'),Point('B'),Point('C'))]
