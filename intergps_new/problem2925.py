import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


relations = [(Length(Point('A'),Point('B')) - sympy.simplify('12')), (Length(Point('A'),Point('D')) - sympy.simplify('10')), Perpendicular(Point('A'),Point('B'),Point('B'),Point('C')), Perpendicular(Point('A'),Point('B'),Point('A'),Point('D')), Perpendicular(Point('B'),Point('C'),Point('C'),Point('D')), Perpendicular(Point('A'),Point('D'),Point('C'),Point('D')), Rectangle(Point('A'),Point('B'),Point('C'),Point('D'))]
goal = Area(Point('A'),Point('B'),Point('C'),Point('D'))
solution = '120'

diagrammatic_relations = {SameSide(Point('A'),Point('B'),Point('C'),Point('D')), NotCollinear(Point('A'),Point('C'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('C')), SameSide(Point('A'),Point('D'),Point('B'),Point('C')), NotCollinear(Point('A'),Point('B'),Point('D')), SameSide(Point('C'),Point('D'),Point('A'),Point('B')), OppositeSide(Point('A'),Point('C'),Point('B'),Point('D')), SameSide(Point('B'),Point('C'),Point('A'),Point('D')), NotCollinear(Point('B'),Point('C'),Point('D')), OppositeSide(Point('B'),Point('D'),Point('A'),Point('C'))}
