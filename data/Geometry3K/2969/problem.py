import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [Perpendicular(Point('B'),Point('A'),Point('A'),Point('E')),Perpendicular(Point('E'),Point('C'),Point('C'),Point('B')), Angle(Point('A'),Point('B'),Point('C'))-sympy.simplify('70*pi/180')]
goal = Angle(Point('A'),Point('E'),Point('C'))
solution = '110*pi/180'

diagrammatic_relations = [NotCollinear(Point('A'),Point('B'),Point('C')), OppositeSide(Point('B'),Point('E'),Point('A'),Point('C')),OppositeSide(Point('A'),Point('C'),Point('B'),Point('E'))]
