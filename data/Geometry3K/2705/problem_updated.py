import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Angle(Point('A'),Point('D'),Point('C')) - ((((sympy.simplify('3') * Variable('y')) + sympy.simplify('36')) / sympy.simplify('180')) * sympy.simplify('pi'))), (Angle(Point('B'),Point('A'),Point('D')) - ((((sympy.simplify('5') * Variable('x')) - sympy.simplify('19')) / sympy.simplify('180')) * sympy.simplify('pi'))), (Angle(Point('B'),Point('C'),Point('D')) - ((((sympy.simplify('3') * Variable('x')) + sympy.simplify('9')) / sympy.simplify('180')) * sympy.simplify('pi'))), (Angle(Point('A'),Point('B'),Point('C')) - ((((sympy.simplify('6') * Variable('y')) - sympy.simplify('57')) / sympy.simplify('180')) * sympy.simplify('pi'))), Parallelogram(Point('A'),Point('B'),Point('C'),Point('D'))]
goal = Variable('y')
solution = '31'

diagrammatic_relations = {SameSide(Point('C'),Point('D'),Point('A'),Point('B')), SameSide(Point('B'),Point('C'),Point('A'),Point('D')), NotCollinear(Point('B'),Point('C'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('D')), OppositeSide(Point('A'),Point('C'),Point('B'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('C')), SameSide(Point('A'),Point('B'),Point('C'),Point('D')), SameSide(Point('A'),Point('D'),Point('B'),Point('C')), OppositeSide(Point('B'),Point('D'),Point('A'),Point('C')), NotCollinear(Point('A'),Point('C'),Point('D'))}
