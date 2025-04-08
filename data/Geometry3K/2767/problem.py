import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Angle(Point('A'),Point('B'),Point('D')) - ((Variable('x') / sympy.simplify('180')) * sympy.simplify('pi'))), (Angle(Point('C'),Point('B'),Point('D')) - sympy.simplify('132/180*pi')), (Angle(Point('A'),Point('B'),Point('C')) - sympy.simplify('65/180*pi')), (Length(Point('A'),Point('B')) - Variable('radius_B')), (Length(Point('B'),Point('C')) - Variable('radius_B')), (Length(Point('B'),Point('D')) - Variable('radius_B'))]
goal = Variable('x')
solution = '163'

diagrammatic_relations = [SameSide(Point('A'),Point('B'),Point('C'),Point('D')), NotCollinear(Point('A'),Point('C'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('C')), NotCollinear(Point('A'),Point('B'),Point('D')), OppositeSide(Point('A'),Point('C'),Point('B'),Point('D')), OppositeSide(Point('C'),Point('D'),Point('A'),Point('B')), NotCollinear(Point('B'),Point('C'),Point('D')), SameSide(Point('B'),Point('C'),Point('A'),Point('D')), OppositeSide(Point('A'),Point('D'),Point('B'),Point('C')), SameSide(Point('B'),Point('D'),Point('A'),Point('C'))]
