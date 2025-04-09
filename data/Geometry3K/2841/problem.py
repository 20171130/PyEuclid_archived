import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('B'),Point('C')) - sympy.simplify('20')), (Length(Point('A'),Point('C')) - sympy.simplify('25')), (Length(Point('A'),Point('B')) - sympy.simplify('15')), Perpendicular(Point('A'),Point('B'),Point('B'),Point('C'))]
goal = sympy.cos(Angle(Point('B'),Point('A'),Point('C')))
solution = '0.60'

diagrammatic_relations = [NotCollinear(Point('A'),Point('B'),Point('C'))]

new_diagrammatic_relations = {NotCollinear(Point('A'),Point('B'),Point('C'))}

