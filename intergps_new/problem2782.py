import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


relations = [(Length(Point('B'),Point('C')) - (sympy.simplify('14') * sympy.sqrt(sympy.simplify('3')))), (Length(Point('A'),Point('B')) - Variable('y')), (Angle(Point('A'),Point('B'),Point('C')) - sympy.simplify('30/180*pi')), (Length(Point('A'),Point('C')) - Variable('x')), Perpendicular(Point('A'),Point('C'),Point('B'),Point('C'))]
goal = Variable('x')
solution = '14'

diagrammatic_relations = {NotCollinear(Point('A'),Point('B'),Point('C'))}
