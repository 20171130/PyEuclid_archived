import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Angle(Point('A'),Point('C'),Point('B')) - sympy.simplify('52/180*pi')), (Length(Point('A'),Point('B')) - Variable('x')), (Length(Point('B'),Point('C')) - sympy.simplify('13')), Perpendicular(Point('A'),Point('B'),Point('B'),Point('C'))]
goal = Variable('x')
solution = '16.64'

diagrammatic_relations = {NotCollinear(Point('A'),Point('B'),Point('C'))}
