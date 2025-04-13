import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('A'),Point('B')) - sympy.simplify('28')), (Length(Point('B'),Point('C')) - sympy.simplify('9')), (Angle(Point('A'),Point('B'),Point('C')) - sympy.simplify('45/180*pi')), Between(Point('E'),Point('A'),Point('B')), Collinear(Point('A'),Point('B'),Point('E')), Perpendicular(Point('A'),Point('E'),Point('C'),Point('E')), Parallelogram(Point('A'),Point('B'),Point('C'),Point('D'))]
goal = Area(Point('A'),Point('B'),Point('C'),Point('D'))
solution = '178.2'

diagrammatic_relations = [ SameSide(Point('C'),Point('D'),Point('A'),Point('B')),   SameSide(Point('A'),Point('B'),Point('C'),Point('D')), SameSide(Point('A'),Point('D'),Point('B'),Point('C')),  OppositeSide(Point('B'),Point('D'),Point('A'),Point('C')),  NotCollinear(Point('A'),Point('B'),Point('D')), OppositeSide(Point('A'),Point('C'),Point('B'),Point('D')), SameSide(Point('B'),Point('C'),Point('A'),Point('D')), NotCollinear(Point('A'),Point('C'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('C')),  NotCollinear(Point('B'),Point('C'),Point('D'))]

new_diagrammatic_relations = {SameSide(Point('C'),Point('D'),Point('A'),Point('B')),   SameSide(Point('A'),Point('B'),Point('C'),Point('D')), SameSide(Point('A'),Point('D'),Point('B'),Point('C')),  OppositeSide(Point('B'),Point('D'),Point('A'),Point('C')),  NotCollinear(Point('A'),Point('B'),Point('D')), OppositeSide(Point('A'),Point('C'),Point('B'),Point('D')), SameSide(Point('B'),Point('C'),Point('A'),Point('D')), NotCollinear(Point('A'),Point('C'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('C')),  NotCollinear(Point('B'),Point('C'),Point('D'))}

