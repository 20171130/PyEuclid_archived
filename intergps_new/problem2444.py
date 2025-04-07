import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


relations = [(Length(Point('B'),Point('D')) - sympy.simplify('22')), (Length(Point('B'),Point('C')) - sympy.simplify('40')), (Angle(Point('A'),Point('C'),Point('B')) - ((Variable('y') / sympy.simplify('180')) * sympy.simplify('pi'))), (Angle(Point('A'),Point('B'),Point('D')) - ((Variable('x') / sympy.simplify('180')) * sympy.simplify('pi'))), Between(Point('A'),Point('C'),Point('D')), Collinear(Point('A'),Point('C'),Point('D')), (Length(Point('A'),Point('D')) - Length(Point('A'),Point('C'))), Perpendicular(Point('A'),Point('D'),Point('B'),Point('D'))]
goal = Variable('x')
solution = '37.2'

diagrammatic_relations = {NotCollinear(Point('A'),Point('B'),Point('C')), SameSide(Point('A'),Point('D'),Point('B'),Point('C')), NotCollinear(Point('A'),Point('B'),Point('D')), OppositeSide(Point('C'),Point('D'),Point('A'),Point('B')), SameSide(Point('A'),Point('C'),Point('B'),Point('D')), NotCollinear(Point('B'),Point('C'),Point('D'))}
