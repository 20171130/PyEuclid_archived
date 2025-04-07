import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


relations = [(Length(Point('B'),Point('C')) - sympy.simplify('34')), (Length(Point('A'),Point('D')) - Variable('x')), Between(Point('D'),Point('B'),Point('C')), Collinear(Point('B'),Point('C'),Point('D')), Perpendicular(Point('A'),Point('D'),Point('C'),Point('D')), (Area(Point('A'),Point('B'),Point('C')) - sympy.simplify('357'))]
goal = Variable('x')
solution = '21'

diagrammatic_relations = {Between(Point('D'),Point('B'),Point('C')), NotCollinear(Point('A'),Point('C'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('C')), NotCollinear(Point('A'),Point('B'),Point('D')), SameSide(Point('C'),Point('D'),Point('A'),Point('B')), OppositeSide(Point('B'),Point('C'),Point('A'),Point('D')), SameSide(Point('B'),Point('D'),Point('A'),Point('C'))}
