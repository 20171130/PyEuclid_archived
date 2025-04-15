import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('B'),Point('D')) - Variable('y')), (Length(Point('C'),Point('D')) - sympy.simplify('6')), (Length(Point('A'),Point('D')) - Variable('x')), (Length(Point('B'),Point('C')) - sympy.simplify('8')), (Length(Point('A'),Point('B')) - Variable('z')), Between(Point('C'),Point('A'),Point('D')), Collinear(Point('A'),Point('C'),Point('D')), Perpendicular(Point('A'),Point('C'),Point('B'),Point('C')), Perpendicular(Point('A'),Point('B'),Point('B'),Point('D'))]
goal = Variable('z')
solution = '(40)/(3)'

diagrammatic_relations = {SameSide(Point('C'),Point('D'),Point('A'),Point('B')), OppositeSide(Point('A'),Point('D'),Point('B'),Point('C')), NotCollinear(Point('B'),Point('C'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('D')), Between(Point('C'),Point('A'),Point('D')), SameSide(Point('A'),Point('C'),Point('B'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('C'))}
