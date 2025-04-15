import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('B'),Point('C')) - sympy.simplify('24')), (Length(Point('A'),Point('C')) - sympy.simplify('74')), (Length(Point('A'),Point('B')) - Variable('x')), Perpendicular(Point('A'),Point('B'),Point('B'),Point('C'))]
goal = Variable('x')
solution = '70'

diagrammatic_relations = [NotCollinear(Point('A'),Point('B'),Point('C'))]

new_diagrammatic_relations = {NotCollinear(Point('A'),Point('B'),Point('C'))}

