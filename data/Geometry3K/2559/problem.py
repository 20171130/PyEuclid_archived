import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('B'),Point('C')) - Variable('y')), (Angle(Point('A'),Point('C'),Point('B')) - sympy.simplify('60/180*pi')), (Length(Point('A'),Point('C')) - Variable('x')), (Length(Point('A'),Point('B')) - (sympy.simplify('8') * sympy.sqrt(sympy.simplify('3')))), Perpendicular(Point('A'),Point('B'),Point('A'),Point('C'))]
goal = Variable('x')
solution = '8'

diagrammatic_relations = [NotCollinear(Point('A'),Point('B'),Point('C'))]
