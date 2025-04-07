import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


relations = [Length(Point('A'),Point('D')) - 88/10, (Length(Point('B'),Point('C')) - 85/10), Between(Point('D'),Point('A'),Point('C')), Collinear(Point('A'),Point('C'),Point('D')), Angle(Point('A'),Point('D'),Point('B'))-pi/2, Angle(Point('A'),Point('B'),Point('C'))-pi/2]
goal = Length(Point('B'),Point('D'))
solution = '6.75'

diagrammatic_relations = {NotCollinear(Point('A'),Point('B'),Point('C'))}