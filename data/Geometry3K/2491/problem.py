import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('A'),Point('B')) - sympy.simplify('26')), (Length(Point('A'),Point('C')) - sympy.simplify('24')), (Length(Point('B'),Point('C')) - sympy.simplify('10')), Perpendicular(Point('A'),Point('C'),Point('B'),Point('C'))]
goal = sympy.cos(Angle(Point('A'),Point('B'),Point('C')))
solution = '0.38'

diagrammatic_relations = [NotCollinear(Point('A'),Point('B'),Point('C'))]

new_diagrammatic_relations = {NotCollinear(Point('A'),Point('B'),Point('C'))}

