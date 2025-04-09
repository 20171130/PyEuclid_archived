import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Angle(Point('B'),Point('C'),Point('D')) - (((sympy.simplify('10') * Variable('y')) / sympy.simplify('180')) * sympy.simplify('pi'))), (Angle(Point('A'),Point('C'),Point('B')) - sympy.simplify('100/180*pi')), (Angle(Point('C'),Point('B'),Point('D')) - (((sympy.simplify('25') * Variable('x')) / sympy.simplify('180')) * sympy.simplify('pi'))), (Angle(Point('A'),Point('B'),Point('C')) - sympy.simplify('40/180*pi')), Parallelogram(Point('A'),Point('B'),Point('D'),Point('C'))]
goal = Variable('x')
solution = '4'

diagrammatic_relations = [SameSide(Point('A'),Point('B'),Point('C'),Point('D')), NotCollinear(Point('A'),Point('C'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('C')), NotCollinear(Point('A'),Point('B'),Point('D')), SameSide(Point('C'),Point('D'),Point('A'),Point('B')), NotCollinear(Point('B'),Point('C'),Point('D')), SameSide(Point('A'),Point('C'),Point('B'),Point('D')), OppositeSide(Point('A'),Point('D'),Point('B'),Point('C')), OppositeSide(Point('B'),Point('C'),Point('A'),Point('D')), SameSide(Point('B'),Point('D'),Point('A'),Point('C'))]

new_diagrammatic_relations = {SameSide(Point('B'),Point('D'),Point('A'),Point('C')), SameSide(Point('C'),Point('D'),Point('A'),Point('B')), OppositeSide(Point('A'),Point('D'),Point('B'),Point('C')), NotCollinear(Point('B'),Point('C'),Point('D')), OppositeSide(Point('B'),Point('C'),Point('A'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('C')), SameSide(Point('A'),Point('C'),Point('B'),Point('D')), SameSide(Point('A'),Point('B'),Point('C'),Point('D')), NotCollinear(Point('A'),Point('C'),Point('D'))}

