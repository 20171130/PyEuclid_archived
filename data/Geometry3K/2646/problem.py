import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('B'),Point('C')) - sympy.simplify('18')), (Length(Point('A'),Point('B')) - sympy.simplify('27')), Perpendicular(Point('A'),Point('C'),Point('B'),Point('C'))]
goal = Angle(Point('B'),Point('A'),Point('C'))
solution = '(41.8)/180*pi'

diagrammatic_relations = [NotCollinear(Point('A'),Point('B'),Point('C'))]

new_diagrammatic_relations = {NotCollinear(Point('A'),Point('B'),Point('C'))}

