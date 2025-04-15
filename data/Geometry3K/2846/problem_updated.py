import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('A'),Point('B')) - Variable('y')), (Length(Point('B'),Point('C')) - Variable('x')), (Angle(Point('A'),Point('B'),Point('C')) - sympy.simplify('30/180*pi')), (Length(Point('A'),Point('C')) - sympy.simplify('24')), Perpendicular(Point('A'),Point('C'),Point('B'),Point('C'))]
goal = Variable('y')
solution = '48'

diagrammatic_relations = {NotCollinear(Point('A'),Point('B'),Point('C'))}
