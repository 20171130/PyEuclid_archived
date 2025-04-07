import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


relations = [(Length(Point('R'),Point('T')) - sympy.simplify('9')), (Length(Point('S'),Point('T')) - sympy.simplify('7')), (Length(Point('R'),Point('S')) - ((sympy.simplify('2') * Variable('z')) - sympy.simplify('15'))), (Angle(Point('R'),Point('T'),Point('S')) - Angle(Point('R'),Point('S'),Point('T')))]
goal = Variable('z')
solution = '12'

diagrammatic_relations = {NotCollinear(Point('R'),Point('S'),Point('T'))}
