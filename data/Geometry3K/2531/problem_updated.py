import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('B'),Point('C')) - sympy.simplify('3.50000000000000')), (Angle(Point('A'),Point('C'),Point('B')) - sympy.simplify('48/180*pi')), (Length(Point('A'),Point('B')) - Length(Point('A'),Point('C')))]
goal = ((Length(Point('A'),Point('B')) + Length(Point('B'),Point('C'))) + Length(Point('A'),Point('C')))
solution = '8.73'

diagrammatic_relations = {NotCollinear(Point('A'),Point('B'),Point('C'))}
