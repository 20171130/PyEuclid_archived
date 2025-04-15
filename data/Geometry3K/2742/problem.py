import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [Length(Point('A'),Point('D')) - 88/10, (Length(Point('B'),Point('C')) - 85/10), Between(Point('D'),Point('A'),Point('C')), Collinear(Point('A'),Point('C'),Point('D')), Angle(Point('A'),Point('D'),Point('B'))-pi/2, Angle(Point('A'),Point('B'),Point('C'))-pi/2]
goal = Length(Point('B'),Point('D'))
solution = '6.75'

diagrammatic_relations = [NotCollinear(Point('A'),Point('B'),Point('C'))]
new_diagrammatic_relations = {SameSide(Point('C'),Point('D'),Point('A'),Point('B')), NotCollinear(Point('B'),Point('C'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('D')), OppositeSide(Point('A'),Point('C'),Point('B'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('C')), SameSide(Point('A'),Point('D'),Point('B'),Point('C')), Between(Point('D'),Point('A'),Point('C'))}

