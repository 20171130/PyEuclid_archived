import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('K'),Point('L')) - sympy.simplify('9')), (Length(Point('J'),Point('K')) - sympy.simplify('14')), Perpendicular(Point('J'),Point('L'),Point('K'),Point('L'))]
goal = Angle(Point('K'),Point('J'),Point('L'))
solution = '(40)/180*pi'

diagrammatic_relations = {NotCollinear(Point('J'),Point('K'),Point('L'))}
