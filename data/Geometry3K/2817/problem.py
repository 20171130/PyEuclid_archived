import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('A'),Point('B')) - sympy.simplify('15')), (Length(Point('A'),Point('C')) - sympy.simplify('9')), (Length(Point('B'),Point('C')) - sympy.simplify('12')), Perpendicular(Point('A'),Point('C'),Point('B'),Point('C'))]
goal = Area(Point('A'),Point('B'),Point('C'))
solution = '54'

diagrammatic_relations = [NotCollinear(Point('A'),Point('B'),Point('C'))]
