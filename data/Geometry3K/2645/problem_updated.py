import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('A'),Point('C')) - Variable('h')), (Length(Point('B'),Point('C')) - sympy.simplify('22')), (Angle(Point('A'),Point('B'),Point('C')) - sympy.simplify('30/180*pi')), Perpendicular(Point('A'),Point('B'),Point('A'),Point('C'))]
goal = Variable('h')
solution = '11'

diagrammatic_relations = {NotCollinear(Point('A'),Point('B'),Point('C'))}
