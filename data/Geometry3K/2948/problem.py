import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('B'),Point('D')) - sympy.simplify('5')), (Length(Point('A'),Point('B')) - sympy.simplify('10')), Between(Point('D'),Point('B'),Point('C')), Collinear(Point('B'),Point('C'),Point('D')), Perpendicular(Point('A'),Point('D'),Point('B'),Point('C')), Perpendicular(Point('A'),Point('B'),Point('A'),Point('C')), Perpendicular(Point('A'),Point('D'),Point('B'),Point('C')), Perpendicular(Point('A'),Point('B'),Point('A'),Point('C'))]
goal = Length(Point('B'),Point('C'))
solution = '20'

diagrammatic_relations = [NotCollinear(Point('A'),Point('C'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('C')), NotCollinear(Point('A'),Point('B'),Point('D')), SameSide(Point('C'),Point('D'),Point('A'),Point('B')), OppositeSide(Point('B'),Point('C'),Point('A'),Point('D')), SameSide(Point('B'),Point('D'),Point('A'),Point('C'))]
