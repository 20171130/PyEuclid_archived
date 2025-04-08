import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Angle(Point('X'),Point('W'),Point('Z')) - (((sympy.simplify('3') * Variable('x')) / sympy.simplify('180')) * sympy.simplify('pi'))), (Angle(Point('W'),Point('Z'),Point('Y')) - (((sympy.simplify('4') * Variable('x')) / sympy.simplify('180')) * sympy.simplify('pi'))), (Angle(Point('W'),Point('X'),Point('Y')) - ((Variable('x') / sympy.simplify('180')) * sympy.simplify('pi'))), (Angle(Point('X'),Point('Y'),Point('Z')) - (((sympy.simplify('2') * Variable('x')) / sympy.simplify('180')) * sympy.simplify('pi')))]
goal = Angle(Point('X'),Point('W'),Point('Z'))
solution = '(108)/180*pi'

diagrammatic_relations = [NotCollinear(Point('W'),Point('X'),Point('Y')), SameSide(Point('Y'),Point('Z'),Point('W'),Point('X')), SameSide(Point('W'),Point('Z'),Point('X'),Point('Y')), OppositeSide(Point('X'),Point('Z'),Point('W'),Point('Y')), OppositeSide(Point('W'),Point('Y'),Point('X'),Point('Z')), NotCollinear(Point('W'),Point('X'),Point('Z')), NotCollinear(Point('X'),Point('Y'),Point('Z')), SameSide(Point('W'),Point('X'),Point('Y'),Point('Z')), NotCollinear(Point('W'),Point('Y'),Point('Z')), SameSide(Point('X'),Point('Y'),Point('W'),Point('Z'))]
