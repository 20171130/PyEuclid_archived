import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


relations = [(Length(Point('B'),Point('C')) - Variable('x')), (Length(Point('B'),Point('C')) - Variable('y')), (Length(Point('A'),Point('C')) - sympy.simplify('10')), (Length(Point('A'),Point('B')) - sympy.simplify('20')), Perpendicular(Point('A'),Point('C'),Point('B'),Point('C'))]
goal = Variable('x')
solution = '10*sqrt(3)'

diagrammatic_relations = {NotCollinear(Point('A'),Point('B'),Point('C'))}
