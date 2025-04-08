import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Angle(Point('B'),Point('A'),Point('C')) - sympy.simplify('25/180*pi')), (Angle(Point('A'),Point('C'),Point('B')) - ((Variable('x') / sympy.simplify('180')) * sympy.simplify('pi'))), (Angle(Point('A'),Point('B'),Point('C')) - sympy.simplify('40/180*pi'))]
goal = Variable('x')
solution = '115'

diagrammatic_relations = [NotCollinear(Point('A'),Point('B'),Point('C'))]
