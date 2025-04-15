import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('A'),Point('B')) - sympy.simplify('13')), (Length(Point('A'),Point('C')) - sympy.simplify('22')), (Length(Point('B'),Point('C')) - Variable('x')), Perpendicular(Point('A'),Point('B'),Point('B'),Point('C'))]
goal = Variable('x')
solution = '3*sqrt(35)'

diagrammatic_relations = {NotCollinear(Point('A'),Point('B'),Point('C'))}
