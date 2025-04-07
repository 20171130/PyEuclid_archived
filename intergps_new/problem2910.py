import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


relations = [(Length(Point('C'),Point('D')) - Variable('x')), (Length(Point('B'),Point('C')) - (sympy.simplify('7') * Variable('x'))), (Length(Point('A'),Point('C')) - Variable('y')), (Length(Point('A'),Point('D')) - sympy.simplify('36')), (Length(Point('A'),Point('B')) - Variable('z')), Between(Point('D'),Point('B'),Point('C')), Collinear(Point('B'),Point('C'),Point('D')), Perpendicular(Point('A'),Point('B'),Point('A'),Point('C')), Perpendicular(Point('A'),Point('D'),Point('B'),Point('D'))]
goal = Variable('x')
solution = '6*sqrt(6)'

diagrammatic_relations = {NotCollinear(Point('A'),Point('C'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('C')), NotCollinear(Point('A'),Point('B'),Point('D')), SameSide(Point('C'),Point('D'),Point('A'),Point('B')), OppositeSide(Point('B'),Point('C'),Point('A'),Point('D')), SameSide(Point('B'),Point('D'),Point('A'),Point('C'))}
