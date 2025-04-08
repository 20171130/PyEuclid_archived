import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('A'),Point('C')) - sympy.simplify('9')), (Length(Point('A'),Point('B')) - sympy.simplify('9')), (Angle(Point('B'),Point('A'),Point('C')) - sympy.simplify('60/180*pi'))]
goal = Length(Point('B'),Point('C'))
solution = '9'

diagrammatic_relations = [NotCollinear(Point('A'),Point('B'),Point('C'))]
