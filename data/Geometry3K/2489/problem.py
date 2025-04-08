import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Angle(Point('Q'),Point('T'),Point('S')) - ((Variable('x') / sympy.simplify('180')) * sympy.simplify('pi'))), (Angle(Point('R'),Point('Q'),Point('T')) - ((((sympy.simplify('2') * Variable('x')) + sympy.simplify('5')) / sympy.simplify('180')) * sympy.simplify('pi'))), (Angle(Point('R'),Point('S'),Point('T')) - ((((sympy.simplify('2') * Variable('x')) + sympy.simplify('7')) / sympy.simplify('180')) * sympy.simplify('pi'))), (Angle(Point('Q'),Point('R'),Point('S')) - ((Variable('x') / sympy.simplify('180')) * sympy.simplify('pi')))]
goal = Angle(Point('Q'),Point('R'),Point('S'))
solution = '(58)/180*pi'

diagrammatic_relations = [SameSide(Point('Q'),Point('R'),Point('S'),Point('T')), SameSide(Point('S'),Point('T'),Point('Q'),Point('R')), NotCollinear(Point('Q'),Point('R'),Point('S')), NotCollinear(Point('Q'),Point('R'),Point('T')), SameSide(Point('Q'),Point('T'),Point('R'),Point('S')), OppositeSide(Point('R'),Point('T'),Point('Q'),Point('S')), NotCollinear(Point('R'),Point('S'),Point('T')), OppositeSide(Point('Q'),Point('S'),Point('R'),Point('T')), SameSide(Point('R'),Point('S'),Point('Q'),Point('T')), NotCollinear(Point('Q'),Point('S'),Point('T'))]
