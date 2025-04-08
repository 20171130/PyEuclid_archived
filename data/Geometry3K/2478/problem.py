import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('Q'),Point('R')) - sympy.simplify('35')), (Length(Point('R'),Point('S')) - sympy.simplify('37')), (Length(Point('L'),Point('N')) - sympy.simplify('5')), (Length(Point('Q'),Point('S')) - sympy.simplify('12')), Similar(Point('L'),Point('M'),Point('N'),Point('Q'),Point('R'),Point('S')), (Length(Point('Q'),Point('R')) - sympy.simplify('35')), (Length(Point('R'),Point('S')) - sympy.simplify('37')), (Length(Point('Q'),Point('S')) - sympy.simplify('12')), (Length(Point('L'),Point('N')) - sympy.simplify('5')), Similar(Point('L'),Point('M'),Point('N'),Point('Q'),Point('R'),Point('S')), (Length(Point('Q'),Point('R')) - sympy.simplify('35')), (Length(Point('R'),Point('S')) - sympy.simplify('37')), (Length(Point('Q'),Point('S')) - sympy.simplify('12')), (Length(Point('L'),Point('N')) - sympy.simplify('5'))]
goal = ((Length(Point('L'),Point('M')) + Length(Point('M'),Point('N'))) + Length(Point('L'),Point('N')))
solution = '35'

diagrammatic_relations = [NotCollinear(Point('Q'),Point('R'),Point('S'))]
