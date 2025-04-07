import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


relations = [(Length(Point('A'),Point('D')) - sympy.simplify('12')), (Length(Point('C'),Point('D')) - (Variable('t') + sympy.simplify('1'))), (Length(Point('B'),Point('D')) - sympy.simplify('24')), Between(Point('D'),Point('B'),Point('C')), Collinear(Point('B'),Point('C'),Point('D')), Perpendicular(Point('A'),Point('D'),Point('B'),Point('D')), Perpendicular(Point('A'),Point('B'),Point('A'),Point('C'))]
goal = Variable('t')
solution = '5'

diagrammatic_relations = {NotCollinear(Point('A'),Point('C'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('C')), NotCollinear(Point('A'),Point('B'),Point('D')), SameSide(Point('C'),Point('D'),Point('A'),Point('B')), OppositeSide(Point('B'),Point('C'),Point('A'),Point('D')), SameSide(Point('B'),Point('D'),Point('A'),Point('C'))}
