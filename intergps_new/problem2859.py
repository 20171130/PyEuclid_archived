import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


relations = [(Length(Point('A'),Point('D')) - sympy.simplify('12')), (Angle(Point('B'),Point('C'),Point('D')) - sympy.simplify('60/180*pi')), (Length(Point('C'),Point('D')) - sympy.simplify('10')), Parallelogram(Point('A'),Point('B'),Point('C'),Point('D'))]
goal = (((Length(Point('A'),Point('D')) + Length(Point('A'),Point('B'))) + Length(Point('B'),Point('C'))) + Length(Point('C'),Point('D')))
solution = '44'

diagrammatic_relations = {SameSide(Point('A'),Point('B'),Point('C'),Point('D')), NotCollinear(Point('A'),Point('C'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('C')), SameSide(Point('A'),Point('D'),Point('B'),Point('C')), NotCollinear(Point('A'),Point('B'),Point('D')), SameSide(Point('C'),Point('D'),Point('A'),Point('B')), OppositeSide(Point('A'),Point('C'),Point('B'),Point('D')), SameSide(Point('B'),Point('C'),Point('A'),Point('D')), NotCollinear(Point('B'),Point('C'),Point('D')), OppositeSide(Point('B'),Point('D'),Point('A'),Point('C'))}
