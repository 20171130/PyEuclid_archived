import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


relations = [(Length(Point('A'),Point('B')) - Variable('x')), (Length(Point('C'),Point('D')) - sympy.simplify('18')), (Length(Point('B'),Point('C')) - sympy.simplify('30')), Between(Point('D'),Point('A'),Point('C')), Collinear(Point('A'),Point('C'),Point('D')), (Length(Point('A'),Point('B')) - Variable('radius_A')), (Length(Point('A'),Point('D')) - Variable('radius_A')), (Angle(Point('A'),Point('B'),Point('C')) - sympy.simplify('pi/2'))]
goal = Variable('x')
solution = '16'

diagrammatic_relations = {NotCollinear(Point('A'),Point('B'),Point('C')), SameSide(Point('A'),Point('D'),Point('B'),Point('C')), NotCollinear(Point('A'),Point('B'),Point('D')), SameSide(Point('C'),Point('D'),Point('A'),Point('B')), OppositeSide(Point('A'),Point('C'),Point('B'),Point('D')), NotCollinear(Point('B'),Point('C'),Point('D'))}
