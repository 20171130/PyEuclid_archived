import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('A'),Point('J')) - sympy.simplify('15')), (Angle(Point('J'),Point('C'),Point('K')) - sympy.simplify('105/180*pi')), Between(Point('C'),Point('A'),Point('J')), Collinear(Point('A'),Point('C'),Point('J')), (Length(Point('A'),Point('C')) - Variable('radius_C')), (Length(Point('C'),Point('J')) - Variable('radius_C')), (Length(Point('C'),Point('K')) - Variable('radius_C'))]
goal = (Angle(Point('J'),Point('C'),Point('K')) * Variable('radius_C'))
solution = '13.74'

diagrammatic_relations = {SameSide(Point('C'),Point('J'),Point('A'),Point('K')), NotCollinear(Point('A'),Point('C'),Point('K')), Between(Point('C'),Point('A'),Point('J')), OppositeSide(Point('A'),Point('J'),Point('C'),Point('K')), SameSide(Point('A'),Point('C'),Point('J'),Point('K')), NotCollinear(Point('A'),Point('J'),Point('K')), NotCollinear(Point('C'),Point('J'),Point('K'))}
