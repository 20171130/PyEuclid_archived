import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


relations = [(Angle(Point('C'),Point('B'),Point('D')) - sympy.simplify('55/180*pi')), (Angle(Point('A'),Point('B'),Point('D')) - ((Variable('x') / sympy.simplify('180')) * sympy.simplify('pi'))), (Angle(Point('B'),Point('A'),Point('D')) - sympy.simplify('69/180*pi')), Perpendicular(Point('B'),Point('C'),Point('C'),Point('D')), (Angle(Point('A'),Point('D'),Point('C')) - sympy.simplify('61/180*pi')), (Angle(Point('A'),Point('D'),Point('C')) - sympy.simplify('61/180*pi'))]
goal = Angle(Point('A'),Point('B'),Point('C'))
solution = '(140)/180*pi'

diagrammatic_relations = {SameSide(Point('A'),Point('B'),Point('C'),Point('D')), NotCollinear(Point('A'),Point('C'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('C')), SameSide(Point('A'),Point('D'),Point('B'),Point('C')), NotCollinear(Point('A'),Point('B'),Point('D')), SameSide(Point('C'),Point('D'),Point('A'),Point('B')), OppositeSide(Point('A'),Point('C'),Point('B'),Point('D')), SameSide(Point('B'),Point('C'),Point('A'),Point('D')), NotCollinear(Point('B'),Point('C'),Point('D')), OppositeSide(Point('B'),Point('D'),Point('A'),Point('C'))}
