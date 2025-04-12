import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Angle(Point('A'),Point('B'),Point('C')) - sympy.simplify('60/180*pi')), (Length(Point('B'),Point('C')) - Variable('y')), (Length(Point('A'),Point('B')) - sympy.simplify('20')), (Length(Point('A'),Point('C')) - Variable('x')), Perpendicular(Point('A'),Point('C'),Point('B'),Point('C'))]
goal = Variable('y')
solution = '10'

diagrammatic_relations = {NotCollinear(Point('A'),Point('B'),Point('C'))}
