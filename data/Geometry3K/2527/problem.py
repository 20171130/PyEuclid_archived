import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('C'),Point('E')) - sympy.simplify('16')), (Length(Point('A'),Point('B')) - sympy.simplify('20')), (Length(Point('A'),Point('D')) - sympy.simplify('18')), Between(Point('E'),Point('A'),Point('D')), Collinear(Point('A'),Point('D'),Point('E')), Perpendicular(Point('C'),Point('E'),Point('D'),Point('E')), Parallelogram(Point('A'),Point('B'),Point('C'),Point('D'))]
goal = (((Length(Point('B'),Point('C')) + Length(Point('C'),Point('D'))) + Length(Point('A'),Point('D'))) + Length(Point('A'),Point('B')))
solution = '76'

diagrammatic_relations = [SameSide(Point('A'),Point('B'),Point('C'),Point('D')), NotCollinear(Point('A'),Point('C'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('C')), SameSide(Point('A'),Point('D'),Point('B'),Point('C')), NotCollinear(Point('A'),Point('B'),Point('D')), SameSide(Point('C'),Point('D'),Point('A'),Point('B')), OppositeSide(Point('A'),Point('C'),Point('B'),Point('D')), SameSide(Point('B'),Point('C'),Point('A'),Point('D')), NotCollinear(Point('B'),Point('C'),Point('D')), OppositeSide(Point('B'),Point('D'),Point('A'),Point('C'))]
