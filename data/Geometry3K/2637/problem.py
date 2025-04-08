import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('A'),Point('C')) - sympy.simplify('12')), (Length(Point('B'),Point('C')) - sympy.simplify('25.5000000000000')), (Length(Point('A'),Point('B')) - Variable('x')), Perpendicular(Point('A'),Point('B'),Point('A'),Point('C'))]
goal = Variable('x')
solution = '22.5'

diagrammatic_relations = [NotCollinear(Point('A'),Point('B'),Point('C'))]
