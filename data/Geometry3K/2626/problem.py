import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('B'),Point('D')) - sympy.simplify('6')), (Length(Point('A'),Point('D')) - sympy.simplify('10')), Perpendicular(Point('B'),Point('D'),Point('C'),Point('D')), Perpendicular(Point('A'),Point('B'),Point('B'),Point('D')), Parallelogram(Point('A'),Point('B'),Point('C'),Point('D'))]
goal = Area(Point('A'),Point('B'),Point('C'),Point('D'))
solution = '48'

diagrammatic_relations = [SameSide(Point('A'),Point('B'),Point('C'),Point('D')), NotCollinear(Point('A'),Point('C'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('C')), SameSide(Point('A'),Point('D'),Point('B'),Point('C')), NotCollinear(Point('A'),Point('B'),Point('D')), SameSide(Point('C'),Point('D'),Point('A'),Point('B')), OppositeSide(Point('A'),Point('C'),Point('B'),Point('D')), SameSide(Point('B'),Point('C'),Point('A'),Point('D')), NotCollinear(Point('B'),Point('C'),Point('D')), OppositeSide(Point('B'),Point('D'),Point('A'),Point('C'))]
