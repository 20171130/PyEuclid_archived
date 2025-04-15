import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Perpendicular(Point('A'),Point('D'),Point('D'),Point('C'))),Perpendicular(Point('D'),Point('C'),Point('C'),Point('B')), (Length(Point('C'),Point('D')) - sympy.simplify('48')), (Length(Point('A'),Point('D')) - sympy.simplify('41')), (Length(Point('B'),Point('C')) - sympy.simplify('53')), Trapezoid(Point('A'),Point('D'),Point('C'),Point('B'))]
goal = Area(Point('A'),Point('B'),Point('C'),Point('D'))
solution = '2256'

diagrammatic_relations = {SameSide(Point('C'),Point('D'),Point('A'),Point('B')), SameSide(Point('B'),Point('C'),Point('A'),Point('D')), NotCollinear(Point('B'),Point('C'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('D')), OppositeSide(Point('A'),Point('C'),Point('B'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('C')), SameSide(Point('A'),Point('B'),Point('C'),Point('D')), SameSide(Point('A'),Point('D'),Point('B'),Point('C')), OppositeSide(Point('B'),Point('D'),Point('A'),Point('C')), NotCollinear(Point('A'),Point('C'),Point('D'))}
