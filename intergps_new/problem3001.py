import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


relations = [(Angle(Point('J'),Point('C'),Point('K')) - sympy.simplify('30/180*pi')), (Length(Point('C'),Point('K')) - sympy.simplify('2')), (Length(Point('C'),Point('K')) - Variable('radius_C')), (Length(Point('C'),Point('J')) - Variable('radius_C'))]
goal = (Angle(Point('J'),Point('C'),Point('K')) * Variable('radius_C'))
solution = '1.05'

diagrammatic_relations = {NotCollinear(Point('C'),Point('J'),Point('K'))}
