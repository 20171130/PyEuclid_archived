import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


relations = [(Length(Point('A'),Point('C')) - Variable('x')), (Length(Point('C'),Point('D')) - sympy.simplify('8')), (Length(Point('B'),Point('D')) - sympy.simplify('16')), (Length(Point('A'),Point('B')) - Variable('y')), (Length(Point('B'),Point('C')) - Variable('z')), Between(Point('D'),Point('A'),Point('C')), Collinear(Point('A'),Point('C'),Point('D')), Perpendicular(Point('A'),Point('D'),Point('B'),Point('D')), Perpendicular(Point('A'),Point('B'),Point('B'),Point('C'))]
goal = Variable('y')
solution = '16*sqrt(5)'

diagrammatic_relations = {NotCollinear(Point('A'),Point('B'),Point('C')), SameSide(Point('A'),Point('D'),Point('B'),Point('C')), NotCollinear(Point('A'),Point('B'),Point('D')), SameSide(Point('C'),Point('D'),Point('A'),Point('B')), OppositeSide(Point('A'),Point('C'),Point('B'),Point('D')), NotCollinear(Point('B'),Point('C'),Point('D'))}
