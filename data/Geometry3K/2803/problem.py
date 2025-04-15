import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('A'),Point('C')) - sympy.simplify('24')), (Length(Point('A'),Point('B')) - Variable('x')), (Angle(Point('A'),Point('B'),Point('C')) - sympy.simplify('61/180*pi')), Perpendicular(Point('A'),Point('C'),Point('B'),Point('C'))]
goal = Variable('x')
solution = '27.44'

diagrammatic_relations = [NotCollinear(Point('A'),Point('B'),Point('C'))]

new_diagrammatic_relations = {NotCollinear(Point('A'),Point('B'),Point('C'))}

