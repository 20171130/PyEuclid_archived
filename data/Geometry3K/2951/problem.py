import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('A'),Point('C')) - sympy.simplify('8')), (Length(Point('B'),Point('C')) - sympy.simplify('10')), (Length(Point('A'),Point('D')) - sympy.simplify('4')), Perpendicular(Point('A'),Point('C'),Point('B'),Point('C')), Perpendicular(Point('A'),Point('C'),Point('A'),Point('D')), Trapezoid(Point('B'),Point('C'),Point('A'),Point('D'))]
goal = (((Length(Point('A'),Point('C')) + Length(Point('B'),Point('C'))) + Length(Point('B'),Point('D'))) + Length(Point('A'),Point('D')))
solution = '32'

diagrammatic_relations = [OppositeSide(Point('A'),Point('B'),Point('C'),Point('D')), NotCollinear(Point('A'),Point('C'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('C')), SameSide(Point('A'),Point('D'),Point('B'),Point('C')), NotCollinear(Point('A'),Point('B'),Point('D')), NotCollinear(Point('B'),Point('C'),Point('D')), OppositeSide(Point('C'),Point('D'),Point('A'),Point('B')), SameSide(Point('A'),Point('C'),Point('B'),Point('D')), SameSide(Point('B'),Point('C'),Point('A'),Point('D')), SameSide(Point('B'),Point('D'),Point('A'),Point('C'))]
