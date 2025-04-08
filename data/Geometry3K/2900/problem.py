import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('A'),Point('B')) - sympy.simplify('5')), (Angle(Point('A'),Point('C'),Point('B')) - sympy.simplify('59/180*pi')), Perpendicular(Point('A'),Point('B'),Point('A'),Point('C'))]
goal = Area(Point('A'),Point('B'),Point('C'))
solution = '7.51'

diagrammatic_relations = [NotCollinear(Point('A'),Point('B'),Point('C'))]
