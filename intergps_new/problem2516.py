import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


relations = [(Length(Point('S'),Point('T')) - sympy.simplify('24.5000000000000')), (Length(Point('T'),Point('V')) - sympy.simplify('24')), (Length(Point('R'),Point('S')) - ((sympy.simplify('2') * Variable('y')) - sympy.simplify('1'))), (Angle(Point('R'),Point('V'),Point('S')) - sympy.simplify('78/180*pi')), (Angle(Point('S'),Point('T'),Point('V')) - ((Variable('x') / sympy.simplify('180')) * sympy.simplify('pi'))), Perpendicular(Point('R'),Point('S'),Point('S'),Point('V')), Congruent(Point('R'),Point('S'),Point('V'),Point('T'),Point('V'),Point('S')), Congruent(Point('R'),Point('S'),Point('V'),Point('T'),Point('V'),Point('S'))]
goal = Variable('x')
solution = '12'

diagrammatic_relations = {SameSide(Point('R'),Point('S'),Point('T'),Point('V')), NotCollinear(Point('R'),Point('S'),Point('V')), NotCollinear(Point('R'),Point('T'),Point('V')), OppositeSide(Point('S'),Point('V'),Point('R'),Point('T')), NotCollinear(Point('S'),Point('T'),Point('V')), NotCollinear(Point('R'),Point('S'),Point('T')), SameSide(Point('S'),Point('T'),Point('R'),Point('V')), OppositeSide(Point('R'),Point('T'),Point('S'),Point('V')), SameSide(Point('R'),Point('V'),Point('S'),Point('T')), SameSide(Point('T'),Point('V'),Point('R'),Point('S'))}
