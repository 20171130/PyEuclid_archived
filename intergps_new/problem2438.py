import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


relations = [(Length(Point('R'),Point('W')) - (Variable('x') + sympy.simplify('6'))), (Length(Point('R'),Point('T')) - ((sympy.simplify('2') * Variable('x')) + sympy.simplify('6'))), (Length(Point('T'),Point('V')) - sympy.simplify('10')), (Length(Point('S'),Point('W')) - sympy.simplify('8')), Between(Point('R'),Point('T'),Point('W')), Collinear(Point('R'),Point('T'),Point('W')), Between(Point('R'),Point('S'),Point('V')), Collinear(Point('R'),Point('S'),Point('V')), (Angle(Point('S'),Point('W'),Point('T')) - Angle(Point('R'),Point('T'),Point('V')))]
goal = Length(Point('R'),Point('W'))
solution = '8'

diagrammatic_relations = {SameSide(Point('R'),Point('S'),Point('T'),Point('V')), OppositeSide(Point('S'),Point('V'),Point('R'),Point('T')), OppositeSide(Point('T'),Point('W'),Point('R'),Point('S')), SameSide(Point('R'),Point('S'),Point('V'),Point('W')), NotCollinear(Point('S'),Point('V'),Point('W')), OppositeSide(Point('S'),Point('V'),Point('T'),Point('W')), SameSide(Point('R'),Point('W'),Point('S'),Point('T')), NotCollinear(Point('R'),Point('T'),Point('V')), NotCollinear(Point('T'),Point('V'),Point('W')), SameSide(Point('S'),Point('T'),Point('V'),Point('W')), NotCollinear(Point('R'),Point('S'),Point('W')), NotCollinear(Point('R'),Point('S'),Point('T')), SameSide(Point('S'),Point('W'),Point('T'),Point('V')), OppositeSide(Point('T'),Point('W'),Point('R'),Point('V')), SameSide(Point('R'),Point('T'),Point('V'),Point('W')), SameSide(Point('R'),Point('V'),Point('S'),Point('T')), SameSide(Point('R'),Point('T'),Point('S'),Point('W')), NotCollinear(Point('R'),Point('V'),Point('W')), NotCollinear(Point('S'),Point('T'),Point('W')), SameSide(Point('R'),Point('V'),Point('S'),Point('W')), SameSide(Point('V'),Point('W'),Point('S'),Point('T')), SameSide(Point('T'),Point('V'),Point('S'),Point('W')), OppositeSide(Point('T'),Point('W'),Point('S'),Point('V')), OppositeSide(Point('S'),Point('V'),Point('R'),Point('W')), NotCollinear(Point('S'),Point('T'),Point('V')), SameSide(Point('R'),Point('W'),Point('T'),Point('V'))}
