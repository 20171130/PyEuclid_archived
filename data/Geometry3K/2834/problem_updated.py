import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('A'),Point('Y')) - sympy.simplify('5')), (Length(Point('A'),Point('N')) - Variable('x')), (Length(Point('A'),Point('B')) - Variable('z')), (Length(Point('N'),Point('Y')) - Variable('y')), (Length(Point('B'),Point('Y')) - sympy.simplify('14')), Between(Point('N'),Point('B'),Point('Y')), Collinear(Point('B'),Point('N'),Point('Y')), Perpendicular(Point('A'),Point('B'),Point('A'),Point('Y')), Perpendicular(Point('A'),Point('N'),Point('B'),Point('N'))]
goal = Variable('z')
solution = '3*sqrt(19)'

diagrammatic_relations = {NotCollinear(Point('A'),Point('B'),Point('N')), NotCollinear(Point('A'),Point('N'),Point('Y')), SameSide(Point('N'),Point('Y'),Point('A'),Point('B')), NotCollinear(Point('A'),Point('B'),Point('Y')), Between(Point('N'),Point('B'),Point('Y')), OppositeSide(Point('B'),Point('Y'),Point('A'),Point('N')), SameSide(Point('B'),Point('N'),Point('A'),Point('Y'))}
