import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


relations = [(Length(Point('B'),Point('D')) - Variable('x')), (Length(Point('B'),Point('C')) - Variable('z')), (Length(Point('A'),Point('D')) - sympy.simplify('4')), (Length(Point('A'),Point('B')) - Variable('y')), (Length(Point('A'),Point('C')) - sympy.simplify('6')), Between(Point('A'),Point('C'),Point('D')), Collinear(Point('A'),Point('C'),Point('D')), Perpendicular(Point('B'),Point('C'),Point('B'),Point('D')), Perpendicular(Point('A'),Point('B'),Point('C'),Point('D'))]
goal = Variable('y')
solution = '2*sqrt(6)'

diagrammatic_relations = {NotCollinear(Point('A'),Point('B'),Point('C')), SameSide(Point('A'),Point('D'),Point('B'),Point('C')), NotCollinear(Point('A'),Point('B'),Point('D')), OppositeSide(Point('C'),Point('D'),Point('A'),Point('B')), SameSide(Point('A'),Point('C'),Point('B'),Point('D')), NotCollinear(Point('B'),Point('C'),Point('D'))}
