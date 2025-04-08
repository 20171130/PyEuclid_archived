import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Angle(Point('A'),Point('B'),Point('C')) - ((Variable('x') / sympy.simplify('180')) * sympy.simplify('pi'))), (Angle(Point('A'),Point('C'),Point('B')) - (((sympy.simplify('2') * Variable('x')) / sympy.simplify('180')) * sympy.simplify('pi'))), Perpendicular(Point('A'),Point('B'),Point('A'),Point('C'))]
goal = Variable('x')
solution = '30'

diagrammatic_relations = [NotCollinear(Point('A'),Point('B'),Point('C'))]
