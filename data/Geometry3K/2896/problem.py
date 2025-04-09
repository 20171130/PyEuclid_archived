import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Angle(Point('J'),Point('K'),Point('L')) - sympy.simplify('109/180*pi')), (Length(Point('L'),Point('M')) - sympy.simplify('6')), Parallelogram(Point('J'),Point('K'),Point('L'),Point('M')), Parallelogram(Point('J'),Point('K'),Point('L'),Point('M'))]
goal = Angle(Point('J'),Point('M'),Point('L'))
solution = '(109)/180*pi'

diagrammatic_relations = [NotCollinear(Point('J'),Point('L'),Point('M')), SameSide(Point('L'),Point('M'),Point('J'),Point('K')), OppositeSide(Point('J'),Point('L'),Point('K'),Point('M')), NotCollinear(Point('J'),Point('K'),Point('L')), SameSide(Point('J'),Point('K'),Point('L'),Point('M')), OppositeSide(Point('K'),Point('M'),Point('J'),Point('L')), SameSide(Point('K'),Point('L'),Point('J'),Point('M')), NotCollinear(Point('J'),Point('K'),Point('M')), NotCollinear(Point('K'),Point('L'),Point('M')), SameSide(Point('J'),Point('M'),Point('K'),Point('L'))]

new_diagrammatic_relations = {SameSide(Point('J'),Point('K'),Point('L'),Point('M')), NotCollinear(Point('J'),Point('L'),Point('M')), OppositeSide(Point('K'),Point('M'),Point('J'),Point('L')), OppositeSide(Point('J'),Point('L'),Point('K'),Point('M')), SameSide(Point('J'),Point('M'),Point('K'),Point('L')), NotCollinear(Point('J'),Point('K'),Point('M')), SameSide(Point('L'),Point('M'),Point('J'),Point('K')), NotCollinear(Point('K'),Point('L'),Point('M')), SameSide(Point('K'),Point('L'),Point('J'),Point('M')), NotCollinear(Point('J'),Point('K'),Point('L'))}

