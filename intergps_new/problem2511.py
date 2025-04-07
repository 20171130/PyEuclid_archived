import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


relations = [(Length(Point('B'),Point('C')) - Variable('x')), (Length(Point('A'),Point('C')) - Variable('x')), (Length(Point('A'),Point('B')) - sympy.simplify('20')), Perpendicular(Point('A'),Point('C'),Point('B'),Point('C'))]
goal = Variable('x')
solution = '14.1'

diagrammatic_relations = {NotCollinear(Point('A'),Point('B'),Point('C'))}
