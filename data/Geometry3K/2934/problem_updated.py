import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('B'),Point('C')) - Variable('y')), (Length(Point('A'),Point('C')) - Variable('x')), (Length(Point('A'),Point('B')) - (sympy.simplify('14') * sympy.sqrt(sympy.simplify('3')))), (Angle(Point('A'),Point('B'),Point('C')) - sympy.simplify('30/180*pi')), Perpendicular(Point('A'),Point('B'),Point('A'),Point('C'))]
goal = Variable('y')
solution = '28'

diagrammatic_relations = {NotCollinear(Point('A'),Point('B'),Point('C'))}
