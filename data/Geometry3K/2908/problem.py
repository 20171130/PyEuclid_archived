import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('K'),Point('M')) - sympy.simplify('20')), (Length(Point('K'),Point('L')) - Variable('z')), (Length(Point('L'),Point('M')) - Variable('x')), (Length(Point('J'),Point('M')) - sympy.simplify('5')), (Length(Point('J'),Point('L')) - Variable('y')), Between(Point('M'),Point('J'),Point('K')), Collinear(Point('J'),Point('K'),Point('M')), Perpendicular(Point('K'),Point('M'),Point('L'),Point('M')), Perpendicular(Point('J'),Point('L'),Point('K'),Point('L'))]
goal = Variable('y')
solution = '5*sqrt(5)'

diagrammatic_relations = [NotCollinear(Point('J'),Point('L'),Point('M')), NotCollinear(Point('J'),Point('K'),Point('L')), OppositeSide(Point('J'),Point('K'),Point('L'),Point('M')), SameSide(Point('K'),Point('M'),Point('J'),Point('L')), NotCollinear(Point('K'),Point('L'),Point('M')), SameSide(Point('J'),Point('M'),Point('K'),Point('L'))]

new_diagrammatic_relations = {OppositeSide(Point('J'),Point('K'),Point('L'),Point('M')), NotCollinear(Point('J'),Point('L'),Point('M')), Between(Point('M'),Point('J'),Point('K')), SameSide(Point('J'),Point('M'),Point('K'),Point('L')), NotCollinear(Point('K'),Point('L'),Point('M')), SameSide(Point('K'),Point('M'),Point('J'),Point('L')), NotCollinear(Point('J'),Point('K'),Point('L'))}

