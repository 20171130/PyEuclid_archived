import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Angle(Point('A'),Point('B'),Point('D')) - ((((sympy.simplify('6') * Variable('y')) + sympy.simplify('16')) / sympy.simplify('180')) * sympy.simplify('pi'))), (Angle(Point('B'),Point('A'),Point('C')) - ((((sympy.simplify('6') * Variable('x')) + sympy.simplify('14')) / sympy.simplify('180')) * sympy.simplify('pi'))), (Angle(Point('A'),Point('C'),Point('D')) - ((((sympy.simplify('7') * Variable('y')) + sympy.simplify('2')) / sympy.simplify('180')) * sympy.simplify('pi'))), (Angle(Point('B'),Point('D'),Point('C')) - ((((sympy.simplify('8') * Variable('x')) - sympy.simplify('8')) / sympy.simplify('180')) * sympy.simplify('pi'))), Parallelogram(Point('A'),Point('B'),Point('D'),Point('C'))]
goal = Variable('y')
solution = '14'

diagrammatic_relations = {SameSide(Point('B'),Point('D'),Point('A'),Point('C')), SameSide(Point('C'),Point('D'),Point('A'),Point('B')), OppositeSide(Point('A'),Point('D'),Point('B'),Point('C')), NotCollinear(Point('B'),Point('C'),Point('D')), OppositeSide(Point('B'),Point('C'),Point('A'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('C')), SameSide(Point('A'),Point('C'),Point('B'),Point('D')), SameSide(Point('A'),Point('B'),Point('C'),Point('D')), NotCollinear(Point('A'),Point('C'),Point('D'))}
