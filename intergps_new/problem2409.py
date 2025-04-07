import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


relations = [(Length(Point('A'),Point('C')) - sympy.simplify('21')), (Angle(Point('A'),Point('C'),Point('B')) - sympy.simplify('60/180*pi')), (Length(Point('A'),Point('B')) - Variable('y')), (Angle(Point('A'),Point('B'),Point('C')) - sympy.simplify('30/180*pi')), (Length(Point('B'),Point('C')) - Variable('x')), Perpendicular(Point('A'),Point('B'),Point('A'),Point('C'))]
goal = Variable('y')
solution = '21*sqrt(3)'

diagrammatic_relations = {NotCollinear(Point('A'),Point('B'),Point('C'))}
