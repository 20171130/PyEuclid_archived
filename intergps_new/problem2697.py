import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


relations = [(Angle(Point('A'),Point('D'),Point('C')) - sympy.simplify('65/180*pi')), (Angle(Point('B'),Point('A'),Point('D')) - ((Variable('x') / sympy.simplify('180')) * sympy.simplify('pi'))), Parallel(Point('A'),Point('B'),Point('C'),Point('D')), Parallel(Point('A'),Point('B'),Point('C'),Point('D')), Parallel(Point('A'),Point('B'),Point('C'),Point('D'))]
goal = Variable('x')
solution = '115'

diagrammatic_relations = {SameSide(Point('A'),Point('B'),Point('C'),Point('D')), NotCollinear(Point('A'),Point('C'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('C')), SameSide(Point('A'),Point('D'),Point('B'),Point('C')), NotCollinear(Point('A'),Point('B'),Point('D')), SameSide(Point('C'),Point('D'),Point('A'),Point('B')), OppositeSide(Point('A'),Point('C'),Point('B'),Point('D')), SameSide(Point('B'),Point('C'),Point('A'),Point('D')), NotCollinear(Point('B'),Point('C'),Point('D')), OppositeSide(Point('B'),Point('D'),Point('A'),Point('C'))}
