import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Angle(Point('K'),Point('L'),Point('M')) - ((((sympy.simplify('2') * Variable('x')) - sympy.simplify('1')) / sympy.simplify('180')) * sympy.simplify('pi'))), (Angle(Point('K'),Point('J'),Point('M')) - sympy.simplify('75/180*pi')), (Angle(Point('J'),Point('M'),Point('L')) - sympy.simplify('105/180*pi')), Parallelogram(Point('J'),Point('K'),Point('L'),Point('M'))]
goal = Variable('x')
solution = '38'

diagrammatic_relations = [NotCollinear(Point('J'),Point('L'),Point('M')), SameSide(Point('L'),Point('M'),Point('J'),Point('K')), OppositeSide(Point('J'),Point('L'),Point('K'),Point('M')), NotCollinear(Point('J'),Point('K'),Point('L')), SameSide(Point('J'),Point('K'),Point('L'),Point('M')), OppositeSide(Point('K'),Point('M'),Point('J'),Point('L')), SameSide(Point('K'),Point('L'),Point('J'),Point('M')), NotCollinear(Point('J'),Point('K'),Point('M')), NotCollinear(Point('K'),Point('L'),Point('M')), SameSide(Point('J'),Point('M'),Point('K'),Point('L'))]

new_diagrammatic_relations = {SameSide(Point('J'),Point('K'),Point('L'),Point('M')), NotCollinear(Point('J'),Point('L'),Point('M')), OppositeSide(Point('K'),Point('M'),Point('J'),Point('L')), OppositeSide(Point('J'),Point('L'),Point('K'),Point('M')), SameSide(Point('J'),Point('M'),Point('K'),Point('L')), NotCollinear(Point('J'),Point('K'),Point('M')), SameSide(Point('L'),Point('M'),Point('J'),Point('K')), NotCollinear(Point('K'),Point('L'),Point('M')), SameSide(Point('K'),Point('L'),Point('J'),Point('M')), NotCollinear(Point('J'),Point('K'),Point('L'))}

