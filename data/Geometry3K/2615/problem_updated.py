import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('A'),Point('C')) - Variable('y')), (Length(Point('A'),Point('B')) - (sympy.simplify('16') * sympy.sqrt(sympy.simplify('3')))), (Length(Point('B'),Point('C')) - Variable('x')), (Angle(Point('B'),Point('A'),Point('C')) - sympy.simplify('60/180*pi')), Perpendicular(Point('A'),Point('C'),Point('B'),Point('C'))]
goal = Variable('y')
solution = '8*sqrt(3)'

diagrammatic_relations = {NotCollinear(Point('A'),Point('B'),Point('C'))}
