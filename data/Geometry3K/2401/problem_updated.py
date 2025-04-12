import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('A'),Point('B')) - sympy.simplify('13')), (Length(Point('B'),Point('C')) - sympy.simplify('13')), (Length(Point('A'),Point('C')) - sympy.simplify('10')), Between(Point('D'),Point('A'),Point('C')), Collinear(Point('A'),Point('C'),Point('D')), Perpendicular(Point('B'),Point('D'),Point('C'),Point('D'))]
goal = Area(Point('A'),Point('B'),Point('C'))
solution = '60'

diagrammatic_relations = {NotCollinear(Point('A'),Point('B'),Point('C'))}
