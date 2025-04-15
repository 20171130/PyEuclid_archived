import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('E'),Point('F')) - sympy.simplify('3')), (Length(Point('D'),Point('E')) - Variable('x')), (Length(Point('B'),Point('C')) - sympy.simplify('15')), (Length(Point('A'),Point('B')) - sympy.simplify('45')), Perpendicular(Point('A'),Point('C'),Point('B'),Point('C')), Perpendicular(Point('D'),Point('F'),Point('E'),Point('F')), (Angle(Point('E'),Point('D'),Point('F')) - Angle(Point('B'),Point('A'),Point('C')))]
goal = Length(Point('D'),Point('E'))
solution = '9'

diagrammatic_relations = {NotCollinear(Point('A'),Point('B'),Point('C'))}
