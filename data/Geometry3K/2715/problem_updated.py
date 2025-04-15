import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Angle(Point('B'),Point('C'),Point('D')) - (((Variable('x') - sympy.simplify('12')) / sympy.simplify('180')) * sympy.simplify('pi'))), (Angle(Point('B'),Point('A'),Point('C')) - ((((sympy.simplify('4') * Variable('x')) - sympy.simplify('8')) / sympy.simplify('180')) * sympy.simplify('pi'))), (Angle(Point('B'),Point('D'),Point('C')) - ((((sympy.simplify('3') * Variable('y')) - sympy.simplify('4')) / sympy.simplify('180')) * sympy.simplify('pi'))), (Angle(Point('A'),Point('B'),Point('C')) - ((((sympy.simplify('1') / sympy.simplify('2')) * Variable('y')) / sympy.simplify('180')) * sympy.simplify('pi'))), Parallelogram(Point('A'),Point('B'),Point('D'),Point('C'))]
goal = Variable('x')
solution = '34'

diagrammatic_relations = {SameSide(Point('B'),Point('D'),Point('A'),Point('C')), SameSide(Point('C'),Point('D'),Point('A'),Point('B')), OppositeSide(Point('A'),Point('D'),Point('B'),Point('C')), NotCollinear(Point('B'),Point('C'),Point('D')), OppositeSide(Point('B'),Point('C'),Point('A'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('C')), SameSide(Point('A'),Point('C'),Point('B'),Point('D')), SameSide(Point('A'),Point('B'),Point('C'),Point('D')), NotCollinear(Point('A'),Point('C'),Point('D'))}
