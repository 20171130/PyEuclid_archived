import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('B'),Point('C')) - Variable('x')), (Length(Point('A'),Point('B')) - sympy.simplify('16')), (Length(Point('A'),Point('C')) - sympy.simplify('4')), Perpendicular(Point('A'),Point('C'),Point('B'),Point('C'))]
goal = Variable('x')
solution = '4*sqrt(15)'

diagrammatic_relations = {NotCollinear(Point('A'),Point('B'),Point('C'))}
