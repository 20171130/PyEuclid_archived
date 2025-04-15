import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('B'),Point('D')) - sympy.simplify('12')), (Length(Point('A'),Point('C')) - sympy.simplify('22')), Rhombus(Point('A'),Point('B'),Point('C'),Point('D'))]
goal = Area(Point('A'),Point('B'),Point('C'),Point('D'))
solution = '132'

diagrammatic_relations = {SameSide(Point('C'),Point('D'),Point('A'),Point('B')), SameSide(Point('B'),Point('C'),Point('A'),Point('D')), NotCollinear(Point('B'),Point('C'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('D')), OppositeSide(Point('A'),Point('C'),Point('B'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('C')), SameSide(Point('A'),Point('B'),Point('C'),Point('D')), SameSide(Point('A'),Point('D'),Point('B'),Point('C')), OppositeSide(Point('B'),Point('D'),Point('A'),Point('C')), NotCollinear(Point('A'),Point('C'),Point('D'))}
