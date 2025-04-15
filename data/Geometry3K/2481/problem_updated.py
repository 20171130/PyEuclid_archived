import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('R'),Point('U')) - (sympy.simplify('3') * Variable('x'))), (Length(Point('R'),Point('U')) - ((sympy.simplify('7') * Variable('x')) - sympy.simplify('44'))), (Length(Point('P'),Point('U')) - Variable('radius_P')), (Length(Point('P'),Point('R')) - Variable('radius_P'))]
goal = Variable('x')
solution = '11'

diagrammatic_relations = {NotCollinear(Point('P'),Point('R'),Point('U'))}
