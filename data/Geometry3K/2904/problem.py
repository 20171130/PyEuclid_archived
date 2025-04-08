import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('A'),Point('C')) - sympy.simplify('5')), (Length(Point('A'),Point('B')) - sympy.simplify('12')), Perpendicular(Point('A'),Point('B'),Point('A'),Point('C'))]
goal = Length(Point('B'),Point('C'))
solution = '13'

diagrammatic_relations = [NotCollinear(Point('A'),Point('B'),Point('C'))]
