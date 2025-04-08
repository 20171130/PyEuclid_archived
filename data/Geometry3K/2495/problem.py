import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('B'),Point('D')) - Variable('y')), (Length(Point('C'),Point('D')) - sympy.simplify('6')), (Length(Point('A'),Point('D')) - Variable('x')), (Length(Point('B'),Point('C')) - sympy.simplify('8')), (Length(Point('A'),Point('B')) - Variable('z')), Between(Point('C'),Point('A'),Point('D')), Collinear(Point('A'),Point('C'),Point('D')), Perpendicular(Point('A'),Point('C'),Point('B'),Point('C')), Perpendicular(Point('A'),Point('B'),Point('B'),Point('D'))]
goal = Variable('z')
solution = '(40)/(3)'

diagrammatic_relations = [NotCollinear(Point('A'),Point('B'),Point('C')), NotCollinear(Point('A'),Point('B'),Point('D')), SameSide(Point('C'),Point('D'),Point('A'),Point('B')), NotCollinear(Point('B'),Point('C'),Point('D')), OppositeSide(Point('A'),Point('D'),Point('B'),Point('C')), SameSide(Point('A'),Point('C'),Point('B'),Point('D'))]
