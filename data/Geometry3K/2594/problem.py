import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('B'),Point('N')) - sympy.simplify('19')), (Length(Point('C'),Point('N')) - sympy.simplify('27')), (Length(Point('A'),Point('B')) - sympy.simplify('41')), (Length(Point('A'),Point('C')) - sympy.simplify('30')), Between(Point('N'),Point('B'),Point('C')), Collinear(Point('B'),Point('C'),Point('N')), Perpendicular(Point('A'),Point('C'),Point('C'),Point('N'))]
goal = Area(Point('A'),Point('B'),Point('N'))
solution = '285'

diagrammatic_relations = [SameSide(Point('C'),Point('N'),Point('A'),Point('B')), NotCollinear(Point('A'),Point('B'),Point('N')), NotCollinear(Point('A'),Point('B'),Point('C')), NotCollinear(Point('A'),Point('C'),Point('N')), SameSide(Point('B'),Point('N'),Point('A'),Point('C')), OppositeSide(Point('B'),Point('C'),Point('A'),Point('N'))]
