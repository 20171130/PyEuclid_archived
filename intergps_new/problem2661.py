import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


relations = [(Length(Point('A'),Point('D')) - sympy.simplify('24')), (Length(Point('B'),Point('D')) - sympy.simplify('14')), Between(Point('D'),Point('A'),Point('B')), Collinear(Point('A'),Point('B'),Point('D')), Perpendicular(Point('A'),Point('D'),Point('C'),Point('D')), Perpendicular(Point('A'),Point('C'),Point('B'),Point('C')), (Length(Point('C'),Point('D')) - Length(Point('A'),Point('B')))]
goal = Length(Point('C'),Point('D'))
solution = '38'

diagrammatic_relations = {OppositeSide(Point('A'),Point('B'),Point('C'),Point('D')), NotCollinear(Point('A'),Point('C'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('C')), SameSide(Point('A'),Point('D'),Point('B'),Point('C')), NotCollinear(Point('B'),Point('C'),Point('D')), SameSide(Point('B'),Point('D'),Point('A'),Point('C'))}
