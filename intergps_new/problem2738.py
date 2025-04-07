import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


relations = [(Length(Point('J'),Point('K')) - sympy.simplify('5')), (Length(Point('J'),Point('L')) - sympy.simplify('13')), (Length(Point('K'),Point('L')) - sympy.simplify('12')), Perpendicular(Point('J'),Point('K'),Point('K'),Point('L'))]
goal = sympy.tan(Angle(Point('J'),Point('L'),Point('K')))
solution = '0.42'

diagrammatic_relations = {NotCollinear(Point('J'),Point('K'),Point('L'))}
