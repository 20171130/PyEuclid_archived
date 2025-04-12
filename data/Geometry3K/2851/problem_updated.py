import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Angle(Point('A'),Point('C'),Point('B')) - sympy.simplify('52/180*pi')), (Angle(Point('B'),Point('A'),Point('C')) - ((Variable('x') / sympy.simplify('180')) * sympy.simplify('pi'))), (Angle(Point('A'),Point('B'),Point('C')) - sympy.simplify('35/180*pi'))]
goal = Variable('x')
solution = '93'

diagrammatic_relations = {NotCollinear(Point('A'),Point('B'),Point('C'))}
