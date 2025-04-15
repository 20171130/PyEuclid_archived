import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [Perpendicular(Point('B'),Point('A'),Point('A'),Point('E')),Perpendicular(Point('E'),Point('C'),Point('C'),Point('B')), Angle(Point('A'),Point('B'),Point('C'))-sympy.simplify('70*pi/180')]
goal = Angle(Point('A'),Point('E'),Point('C'))
solution = '110*pi/180'

diagrammatic_relations = [NotCollinear(Point('A'),Point('B'),Point('C')), OppositeSide(Point('B'),Point('E'),Point('A'),Point('C')),OppositeSide(Point('A'),Point('C'),Point('B'),Point('E'))]

new_diagrammatic_relations = {SameSide(Point('A'),Point('B'),Point('D'),Point('E')), NotCollinear(Point('A'),Point('D'),Point('E')), NotCollinear(Point('B'),Point('C'),Point('D')), SameSide(Point('D'),Point('E'),Point('A'),Point('C')), OppositeSide(Point('B'),Point('C'),Point('D'),Point('E')), NotCollinear(Point('B'),Point('D'),Point('E')), NotCollinear(Point('B'),Point('C'),Point('E')), OppositeSide(Point('B'),Point('D'),Point('A'),Point('C')), OppositeSide(Point('A'),Point('D'),Point('C'),Point('E')), OppositeSide(Point('A'),Point('E'),Point('B'),Point('D')), NotCollinear(Point('C'),Point('D'),Point('E')), SameSide(Point('C'),Point('D'),Point('A'),Point('B')), OppositeSide(Point('B'),Point('E'),Point('A'),Point('C')), OppositeSide(Point('C'),Point('D'),Point('A'),Point('E')), OppositeSide(Point('B'),Point('D'),Point('C'),Point('E')), SameSide(Point('A'),Point('D'),Point('B'),Point('C')), SameSide(Point('A'),Point('B'),Point('C'),Point('D')), OppositeSide(Point('A'),Point('C'),Point('B'),Point('E')), SameSide(Point('B'),Point('E'),Point('A'),Point('D')), SameSide(Point('A'),Point('B'),Point('C'),Point('E')), SameSide(Point('B'),Point('E'),Point('C'),Point('D')), SameSide(Point('D'),Point('E'),Point('A'),Point('B')), SameSide(Point('B'),Point('C'),Point('A'),Point('E')), SameSide(Point('C'),Point('E'),Point('A'),Point('B')), SameSide(Point('A'),Point('D'),Point('B'),Point('E')), NotCollinear(Point('A'),Point('C'),Point('E')), SameSide(Point('A'),Point('E'),Point('C'),Point('D')), SameSide(Point('A'),Point('E'),Point('B'),Point('C')), NotCollinear(Point('A'),Point('C'),Point('D')), SameSide(Point('B'),Point('C'),Point('A'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('D')), OppositeSide(Point('A'),Point('C'),Point('B'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('E')), OppositeSide(Point('C'),Point('D'),Point('B'),Point('E')), OppositeSide(Point('B'),Point('D'),Point('A'),Point('E')), SameSide(Point('C'),Point('E'),Point('A'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('C')), OppositeSide(Point('A'),Point('C'),Point('D'),Point('E')), SameSide(Point('C'),Point('E'),Point('B'),Point('D')), SameSide(Point('D'),Point('E'),Point('B'),Point('C'))}

