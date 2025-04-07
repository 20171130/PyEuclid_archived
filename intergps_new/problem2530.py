import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


relations = [(Length(Point('J'),Point('M')) - sympy.simplify('6')), (Angle(Point('J'),Point('M'),Point('L')) - sympy.simplify('80/180*pi')), (Length(Point('K'),Point('L')) - sympy.simplify('6')), Parallel(Point('J'),Point('K'),Point('L'),Point('M'))]
goal = Angle(Point('J'),Point('K'),Point('L'))
solution = '(100)/180*pi'

diagrammatic_relations = {NotCollinear(Point('J'),Point('L'),Point('M')), SameSide(Point('L'),Point('M'),Point('J'),Point('K')), OppositeSide(Point('J'),Point('L'),Point('K'),Point('M')), NotCollinear(Point('J'),Point('K'),Point('L')), SameSide(Point('J'),Point('K'),Point('L'),Point('M')), OppositeSide(Point('K'),Point('M'),Point('J'),Point('L')), SameSide(Point('K'),Point('L'),Point('J'),Point('M')), NotCollinear(Point('J'),Point('K'),Point('M')), NotCollinear(Point('K'),Point('L'),Point('M')), SameSide(Point('J'),Point('M'),Point('K'),Point('L'))}
