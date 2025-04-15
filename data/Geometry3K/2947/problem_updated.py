import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('A'),Point('B')) - Variable('x')), (Length(Point('B'),Point('C')) - (sympy.simplify('18') * sympy.sqrt(sympy.simplify('3')))), (Angle(Point('B'),Point('A'),Point('C')) - sympy.simplify('45/180*pi')), (Length(Point('A'),Point('C')) - (sympy.simplify('18') * sympy.sqrt(sympy.simplify('3')))), Perpendicular(Point('A'),Point('C'),Point('B'),Point('C'))]
goal = Variable('x')
solution = '18*sqrt(6)'

diagrammatic_relations = {NotCollinear(Point('A'),Point('B'),Point('C'))}
