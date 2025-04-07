import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


relations = [(Length(Point('A'),Point('C')) - Variable('x')), (Length(Point('B'),Point('C')) - Variable('y')), (Angle(Point('B'),Point('A'),Point('C')) - sympy.simplify('60/180*pi')), (Length(Point('A'),Point('B')) - sympy.simplify('10')), Perpendicular(Point('A'),Point('C'),Point('B'),Point('C'))]
goal = Variable('x')
solution = '5'

diagrammatic_relations = {NotCollinear(Point('A'),Point('B'),Point('C'))}
