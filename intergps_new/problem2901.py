import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


relations = [(Angle(Point('W'),Point('X'),Point('Y')) - ((((sympy.simplify('20') * Variable('y')) + sympy.simplify('10')) / sympy.simplify('180')) * sympy.simplify('pi'))), (Length(Point('X'),Point('Z')) - ((sympy.simplify('3') * Variable('y')) + sympy.simplify('7'))), (Length(Point('X'),Point('Y')) - sympy.simplify('19')), Between(Point('X'),Point('Y'),Point('Z')), Collinear(Point('X'),Point('Y'),Point('Z')), Perpendicular(Point('W'),Point('X'),Point('X'),Point('Z')), Congruent(Point('W'),Point('X'),Point('Y'),Point('W'),Point('X'),Point('Z')), Congruent(Point('W'),Point('X'),Point('Y'),Point('W'),Point('X'),Point('Z'))]
goal = Variable('y')
solution = '4'

diagrammatic_relations = {NotCollinear(Point('W'),Point('X'),Point('Y')), NotCollinear(Point('W'),Point('X'),Point('Z')), NotCollinear(Point('W'),Point('Y'),Point('Z')), Between(Point('X'),Point('Y'),Point('Z')), SameSide(Point('X'),Point('Z'),Point('W'),Point('Y')), SameSide(Point('X'),Point('Y'),Point('W'),Point('Z')), OppositeSide(Point('Y'),Point('Z'),Point('W'),Point('X'))}
