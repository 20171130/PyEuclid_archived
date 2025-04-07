import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


relations = [(Angle(Point('A'),Point('C'),Point('D')) - sympy.simplify('148/180*pi')), (Angle(Point('B'),Point('A'),Point('C')) - ((((sympy.simplify('2') * Variable('x')) - sympy.simplify('15')) / sympy.simplify('180')) * sympy.simplify('pi'))), (Angle(Point('A'),Point('B'),Point('D')) - (((Variable('x') - sympy.simplify('5')) / sympy.simplify('180')) * sympy.simplify('pi'))), Between(Point('C'),Point('B'),Point('D')), Collinear(Point('B'),Point('C'),Point('D'))]
goal = Angle(Point('A'),Point('B'),Point('C'))
solution = '(51)/180*pi'

diagrammatic_relations = {NotCollinear(Point('A'),Point('C'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('C')), NotCollinear(Point('A'),Point('B'),Point('D')), SameSide(Point('C'),Point('D'),Point('A'),Point('B')), SameSide(Point('B'),Point('C'),Point('A'),Point('D')), OppositeSide(Point('B'),Point('D'),Point('A'),Point('C'))}
