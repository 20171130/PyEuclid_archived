import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


relations = [(Angle(Point('A'),Point('C'),Point('B')) - sympy.simplify('21/180*pi')), (Length(Point('A'),Point('B')) - sympy.simplify('11')), (Length(Point('A'),Point('C')) - Variable('x')), Perpendicular(Point('A'),Point('B'),Point('B'),Point('C'))]
goal = Variable('x')
solution = '30.7'

diagrammatic_relations = {NotCollinear(Point('A'),Point('B'),Point('C'))}
