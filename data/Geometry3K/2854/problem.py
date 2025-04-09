import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('A'),Point('B')) - Variable('h')), (Angle(Point('A'),Point('B'),Point('C')) - sympy.simplify('60/180*pi')), (Length(Point('B'),Point('C')) - sympy.simplify('4')), Perpendicular(Point('A'),Point('C'),Point('B'),Point('C'))]
goal = Variable('h')
solution = '8'

diagrammatic_relations = [NotCollinear(Point('A'),Point('B'),Point('C'))]

new_diagrammatic_relations = {NotCollinear(Point('A'),Point('B'),Point('C'))}

