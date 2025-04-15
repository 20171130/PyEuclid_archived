import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Angle(Point('A'),Point('C'),Point('D')) - sympy.simplify('148/180*pi')), (Angle(Point('B'),Point('A'),Point('C')) - ((((sympy.simplify('2') * Variable('x')) - sympy.simplify('15')) / sympy.simplify('180')) * sympy.simplify('pi'))), (Angle(Point('A'),Point('B'),Point('D')) - (((Variable('x') - sympy.simplify('5')) / sympy.simplify('180')) * sympy.simplify('pi'))), Between(Point('C'),Point('B'),Point('D')), Collinear(Point('B'),Point('C'),Point('D'))]
goal = Angle(Point('A'),Point('B'),Point('C'))
solution = '(51)/180*pi'

diagrammatic_relations = {SameSide(Point('C'),Point('D'),Point('A'),Point('B')), SameSide(Point('B'),Point('C'),Point('A'),Point('D')), Between(Point('C'),Point('B'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('C')), OppositeSide(Point('B'),Point('D'),Point('A'),Point('C')), NotCollinear(Point('A'),Point('C'),Point('D'))}
