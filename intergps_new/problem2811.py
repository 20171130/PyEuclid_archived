import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


relations = [(Length(Point('A'),Point('C')) - sympy.simplify('16')), (Length(Point('B'),Point('C')) - sympy.simplify('10')), (Angle(Point('A'),Point('B'),Point('C')) - ((Variable('x') / sympy.simplify('180')) * sympy.simplify('pi'))), Perpendicular(Point('A'),Point('C'),Point('B'),Point('C'))]
goal = Variable('x')
solution = '58'

diagrammatic_relations = {NotCollinear(Point('A'),Point('B'),Point('C'))}
