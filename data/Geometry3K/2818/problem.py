import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Angle(Point('A'),Point('B'),Point('C')) - sympy.simplify('30/180*pi')), (Length(Point('B'),Point('C')) - (sympy.simplify('10') * sympy.sqrt(sympy.simplify('3')))), (Length(Point('A'),Point('C')) - Variable('x')), (Length(Point('A'),Point('B')) - Variable('y')), Perpendicular(Point('A'),Point('C'),Point('B'),Point('C'))]
goal = Variable('x')
solution = '10'

diagrammatic_relations = [NotCollinear(Point('A'),Point('B'),Point('C'))]
