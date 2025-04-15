import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('B'),Point('C')) - Variable('y')), (Length(Point('C'),Point('D')) - sympy.simplify('16')), (Length(Point('B'),Point('D')) - sympy.simplify('8')), (Length(Point('B'),Point('C')) - Variable('x')), Perpendicular(Point('B'),Point('C'),Point('B'),Point('D'))]
goal = Variable('x')
solution = '8*sqrt(3)'

diagrammatic_relations = [OppositeSide(Point('A'),Point('B'),Point('C'),Point('D')), NotCollinear(Point('A'),Point('C'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('C')), SameSide(Point('A'),Point('D'),Point('B'),Point('C')), NotCollinear(Point('A'),Point('B'),Point('D')), NotCollinear(Point('B'),Point('C'),Point('D')), OppositeSide(Point('C'),Point('D'),Point('A'),Point('B')), SameSide(Point('A'),Point('C'),Point('B'),Point('D')), SameSide(Point('B'),Point('C'),Point('A'),Point('D')), SameSide(Point('B'),Point('D'),Point('A'),Point('C'))]

new_diagrammatic_relations = {SameSide(Point('B'),Point('D'),Point('A'),Point('C')), SameSide(Point('B'),Point('C'),Point('A'),Point('D')), NotCollinear(Point('B'),Point('C'),Point('D')), OppositeSide(Point('C'),Point('D'),Point('A'),Point('B')), OppositeSide(Point('A'),Point('B'),Point('C'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('C')), SameSide(Point('A'),Point('C'),Point('B'),Point('D')), SameSide(Point('A'),Point('D'),Point('B'),Point('C')), NotCollinear(Point('A'),Point('C'),Point('D'))}

