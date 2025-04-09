import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Angle(Point('M'),Point('N'),Point('P')) - Angle(Point('M'),Point('Q'),Point('P'))), (Angle(Point('N'),Point('P'),Point('Q')) - Angle(Point('N'),Point('M'),Point('Q'))), Parallelogram(Point('M'),Point('N'),Point('P'),Point('Q')), (Angle(Point('N'),Point('M'),Point('Q')) - (((sympy.simplify('10') * Variable('x')) / sympy.simplify('180')) * sympy.simplify('pi'))), (Angle(Point('M'),Point('N'),Point('P')) - (((sympy.simplify('20') * Variable('x')) / sympy.simplify('180')) * sympy.simplify('pi'))), Parallelogram(Point('M'),Point('N'),Point('P'),Point('Q')), (Angle(Point('N'),Point('M'),Point('Q')) - (((sympy.simplify('10') * Variable('x')) / sympy.simplify('180')) * sympy.simplify('pi'))), (Angle(Point('M'),Point('N'),Point('P')) - (((sympy.simplify('20') * Variable('x')) / sympy.simplify('180')) * sympy.simplify('pi')))]
goal = Angle(Point('N'),Point('M'),Point('Q'))
solution = '(60)/180*pi'

diagrammatic_relations = [NotCollinear(Point('M'),Point('N'),Point('Q')), SameSide(Point('N'),Point('P'),Point('M'),Point('Q')), OppositeSide(Point('N'),Point('Q'),Point('M'),Point('P')), OppositeSide(Point('M'),Point('P'),Point('N'),Point('Q')), SameSide(Point('M'),Point('Q'),Point('N'),Point('P')), SameSide(Point('P'),Point('Q'),Point('M'),Point('N')), NotCollinear(Point('M'),Point('N'),Point('P')), SameSide(Point('M'),Point('N'),Point('P'),Point('Q')), NotCollinear(Point('N'),Point('P'),Point('Q')), NotCollinear(Point('M'),Point('P'),Point('Q'))]

new_diagrammatic_relations = {NotCollinear(Point('N'),Point('P'),Point('Q')), OppositeSide(Point('N'),Point('Q'),Point('M'),Point('P')), SameSide(Point('N'),Point('P'),Point('M'),Point('Q')), SameSide(Point('M'),Point('Q'),Point('N'),Point('P')), NotCollinear(Point('M'),Point('N'),Point('Q')), NotCollinear(Point('M'),Point('P'),Point('Q')), OppositeSide(Point('M'),Point('P'),Point('N'),Point('Q')), SameSide(Point('P'),Point('Q'),Point('M'),Point('N')), SameSide(Point('M'),Point('N'),Point('P'),Point('Q')), NotCollinear(Point('M'),Point('N'),Point('P'))}

