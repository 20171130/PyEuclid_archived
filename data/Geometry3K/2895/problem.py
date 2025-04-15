import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('A'),Point('D')) - sympy.simplify('3')), (Length(Point('B'),Point('D')) - sympy.simplify('12')), (Length(Point('A'),Point('C')) - Variable('y')), (Length(Point('C'),Point('D')) - Variable('x')), (Length(Point('B'),Point('C')) - Variable('z')), Between(Point('D'),Point('A'),Point('B')), Collinear(Point('A'),Point('B'),Point('D')), Perpendicular(Point('A'),Point('D'),Point('C'),Point('D')), Perpendicular(Point('A'),Point('C'),Point('B'),Point('C'))]
goal = Variable('z')
solution = '6*sqrt(5)'

diagrammatic_relations = [OppositeSide(Point('A'),Point('B'),Point('C'),Point('D')), NotCollinear(Point('A'),Point('C'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('C')), Between(Point('D'),Point('A'),Point('B')), SameSide(Point('A'),Point('D'),Point('B'),Point('C')), NotCollinear(Point('B'),Point('C'),Point('D')), SameSide(Point('B'),Point('D'),Point('A'),Point('C'))]

new_diagrammatic_relations = {Between(Point('D'),Point('A'),Point('B')), SameSide(Point('B'),Point('D'),Point('A'),Point('C')), NotCollinear(Point('B'),Point('C'),Point('D')), OppositeSide(Point('A'),Point('B'),Point('C'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('C')), SameSide(Point('A'),Point('D'),Point('B'),Point('C')), NotCollinear(Point('A'),Point('C'),Point('D'))}

