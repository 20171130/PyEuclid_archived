import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('A'),Point('C')) - sympy.simplify('12')), Square(Point('A'),Point('C'),Point('B'),Point('D')), (Length(Point('A'),Point('B')) - Variable('y')), Perpendicular(Point('B'),Point('C'),Point('B'),Point('D')), (Length(Point('A'),Point('D')) - Length(Point('B'),Point('D')))]
goal = Variable('y')
solution = '12*sqrt(2)'

diagrammatic_relations = [OppositeSide(Point('A'),Point('B'),Point('C'),Point('D')), NotCollinear(Point('A'),Point('C'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('C')), SameSide(Point('A'),Point('D'),Point('B'),Point('C')), NotCollinear(Point('A'),Point('B'),Point('D')), NotCollinear(Point('B'),Point('C'),Point('D')), OppositeSide(Point('C'),Point('D'),Point('A'),Point('B')), SameSide(Point('A'),Point('C'),Point('B'),Point('D')), SameSide(Point('B'),Point('C'),Point('A'),Point('D')), SameSide(Point('B'),Point('D'),Point('A'),Point('C'))]
