import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('A'),Point('B')) - sympy.simplify('15')), (Length(Point('A'),Point('C')) - Variable('x')), (Length(Point('C'),Point('D')) - sympy.simplify('16')), Between(Point('B'),Point('C'),Point('D')), Collinear(Point('B'),Point('C'),Point('D')), (Length(Point('B'),Point('C')) - Length(Point('B'),Point('D'))), Perpendicular(Point('A'),Point('B'),Point('B'),Point('D'))]
goal = Variable('x')
solution = '17'

diagrammatic_relations = [NotCollinear(Point('A'),Point('C'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('C')), NotCollinear(Point('A'),Point('B'),Point('D')), OppositeSide(Point('C'),Point('D'),Point('A'),Point('B')), SameSide(Point('B'),Point('C'),Point('A'),Point('D')), SameSide(Point('B'),Point('D'),Point('A'),Point('C'))]
