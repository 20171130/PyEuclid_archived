import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('B'),Point('X')) - 36), (Length(Point('A'),Point('B')) - Variable('z')), (Length(Point('C'),Point('X')) - Variable('x')), (Length(Point('A'),Point('C')) - ( Variable('x') * 7)), (Length(Point('B'),Point('C')) - Variable('y')), Between(Point('X'),Point('A'),Point('C')), Collinear(Point('A'),Point('C'),Point('X')), Perpendicular(Point('A'),Point('B'),Point('B'),Point('C')), Perpendicular(Point('A'),Point('X'),Point('X'),Point('B'))]
goal = Variable('z')
solution = '36*sqrt(7)'

diagrammatic_relations = [OppositeSide(Point('A'),Point('C'),Point('B'),Point('X')), SameSide(Point('C'),Point('X'),Point('A'),Point('B')), NotCollinear(Point('A'),Point('B'),Point('C')), NotCollinear(Point('B'),Point('C'),Point('X')), SameSide(Point('A'),Point('X'),Point('B'),Point('C')), NotCollinear(Point('A'),Point('B'),Point('X'))]

new_diagrammatic_relations = {Between(Point('X'),Point('A'),Point('C')), NotCollinear(Point('B'),Point('C'),Point('X')), SameSide(Point('A'),Point('X'),Point('B'),Point('C')), NotCollinear(Point('A'),Point('B'),Point('X')), SameSide(Point('C'),Point('X'),Point('A'),Point('B')), NotCollinear(Point('A'),Point('B'),Point('C')), OppositeSide(Point('A'),Point('C'),Point('B'),Point('X'))}

