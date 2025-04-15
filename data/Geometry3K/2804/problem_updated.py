import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('A'),Point('D')) - sympy.simplify('17')), (Length(Point('D'),Point('E')) - sympy.simplify('8')), (Length(Point('A'),Point('C')) - sympy.simplify('21')), Perpendicular(Point('A'),Point('C'),Point('A'),Point('E')), Between(Point('E'),Point('B'),Point('D')), Collinear(Point('B'),Point('D'),Point('E')), Perpendicular(Point('A'),Point('E'),Point('D'),Point('E')), Parallelogram(Point('A'),Point('C'),Point('B'),Point('D'))]
goal = (((Length(Point('A'),Point('C')) + Length(Point('B'),Point('C'))) + Length(Point('B'),Point('D'))) + Length(Point('A'),Point('D')))
solution = '76'

diagrammatic_relations = {SameSide(Point('B'),Point('D'),Point('A'),Point('C')), SameSide(Point('B'),Point('C'),Point('A'),Point('D')), NotCollinear(Point('B'),Point('C'),Point('D')), OppositeSide(Point('C'),Point('D'),Point('A'),Point('B')), OppositeSide(Point('A'),Point('B'),Point('C'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('C')), SameSide(Point('A'),Point('C'),Point('B'),Point('D')), SameSide(Point('A'),Point('D'),Point('B'),Point('C')), NotCollinear(Point('A'),Point('C'),Point('D'))}
