import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Angle(Point('W'),Point('X'),Point('Y')) - ((Variable('a') / sympy.simplify('180')) * sympy.simplify('pi'))), (Angle(Point('W'),Point('Z'),Point('Y')) - (((Variable('a') + sympy.simplify('2')) / sympy.simplify('180')) * sympy.simplify('pi'))), (Angle(Point('X'),Point('W'),Point('Z')) - (((((sympy.simplify('1') / sympy.simplify('2')) * Variable('a')) + sympy.simplify('8')) / sympy.simplify('180')) * sympy.simplify('pi'))), (Angle(Point('X'),Point('Y'),Point('Z')) - (((Variable('a') - sympy.simplify('28')) / sympy.simplify('180')) * sympy.simplify('pi')))]
goal = Angle(Point('W'),Point('Z'),Point('Y'))
solution = '(110)/180*pi'

diagrammatic_relations = {OppositeSide(Point('W'),Point('Y'),Point('X'),Point('Z')), NotCollinear(Point('W'),Point('X'),Point('Z')), NotCollinear(Point('W'),Point('X'),Point('Y')), SameSide(Point('Y'),Point('Z'),Point('W'),Point('X')), NotCollinear(Point('W'),Point('Y'),Point('Z')), OppositeSide(Point('X'),Point('Z'),Point('W'),Point('Y')), SameSide(Point('W'),Point('Z'),Point('X'),Point('Y')), SameSide(Point('W'),Point('X'),Point('Y'),Point('Z')), NotCollinear(Point('X'),Point('Y'),Point('Z')), SameSide(Point('X'),Point('Y'),Point('W'),Point('Z'))}
