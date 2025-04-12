import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('C'),Point('K')) - sympy.simplify('5')), (Length(Point('B'),Point('C')) - Variable('x')), (Length(Point('A'),Point('B')) - sympy.simplify('2')), Between(Point('B'),Point('A'),Point('K')), Collinear(Point('A'),Point('B'),Point('K')), Perpendicular(Point('B'),Point('C'),Point('B'),Point('K')), (Length(Point('A'),Point('K')) - Variable('radius_K')), (Length(Point('C'),Point('K')) - Variable('radius_K'))]
goal = Length(Point('B'),Point('C'))
solution = '4'

diagrammatic_relations = {NotCollinear(Point('A'),Point('C'),Point('K')), SameSide(Point('A'),Point('B'),Point('C'),Point('K')), OppositeSide(Point('A'),Point('K'),Point('B'),Point('C')), NotCollinear(Point('B'),Point('C'),Point('K')), NotCollinear(Point('A'),Point('B'),Point('C')), Between(Point('B'),Point('A'),Point('K')), SameSide(Point('B'),Point('K'),Point('A'),Point('C'))}
