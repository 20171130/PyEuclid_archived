import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('B'),Point('C')) - sympy.simplify('12')), (Length(Point('B'),Point('D')) - sympy.simplify('8')), (Length(Point('A'),Point('D')) - Variable('y')), (Length(Point('A'),Point('B')) - Variable('x')), (Length(Point('A'),Point('C')) - Variable('z')), Between(Point('D'),Point('B'),Point('C')), Collinear(Point('B'),Point('C'),Point('D')), Perpendicular(Point('A'),Point('D'),Point('C'),Point('D')), Perpendicular(Point('A'),Point('B'),Point('A'),Point('C'))]
goal = Variable('y')
solution = '4*sqrt(2)'

diagrammatic_relations = [NotCollinear(Point('A'),Point('C'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('C')), NotCollinear(Point('A'),Point('B'),Point('D')), SameSide(Point('C'),Point('D'),Point('A'),Point('B')), OppositeSide(Point('B'),Point('C'),Point('A'),Point('D')), SameSide(Point('B'),Point('D'),Point('A'),Point('C'))]

new_diagrammatic_relations = {SameSide(Point('B'),Point('D'),Point('A'),Point('C')), SameSide(Point('C'),Point('D'),Point('A'),Point('B')), Between(Point('D'),Point('B'),Point('C')), OppositeSide(Point('B'),Point('C'),Point('A'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('C')), NotCollinear(Point('A'),Point('C'),Point('D'))}

