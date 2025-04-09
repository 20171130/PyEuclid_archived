import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('A'),Point('B')) - sympy.simplify('3')), (Length(Point('B'),Point('C')) - sympy.simplify('5')), Perpendicular(Point('A'),Point('B'),Point('A'),Point('C'))]
goal = sympy.cos(Angle(Point('A'),Point('C'),Point('B')))
solution = '(4)/(5)'

diagrammatic_relations = [NotCollinear(Point('A'),Point('B'),Point('C'))]

new_diagrammatic_relations = {NotCollinear(Point('A'),Point('B'),Point('C'))}

