import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('Q'),Point('T')) - Variable('x')), (Length(Point('J'),Point('K')) - sympy.simplify('5')), (Area(Point('J'),Point('K'),Point('L'),Point('M')) - sympy.simplify('138')), Trapezoid(Point('J'),Point('K'),Point('L'),Point('M')), (Area(Point('Q'),Point('R'),Point('S'),Point('T')) - sympy.simplify('5.52000000000000')), Trapezoid(Point('Q'),Point('R'),Point('S'),Point('T')), Trapezoid(Point('J'),Point('K'),Point('L'),Point('M')), Trapezoid(Point('Q'),Point('R'),Point('S'),Point('T')), Similar4P(Point('J'),Point('K'),Point('L'),Point('M'),Point('Q'),Point('T'),Point('S'),Point('R')), (Area(Point('J'),Point('K'),Point('L'),Point('M')) - sympy.simplify('138')), Trapezoid(Point('J'),Point('K'),Point('L'),Point('M')), (Area(Point('Q'),Point('R'),Point('S'),Point('T')) - sympy.simplify('552/100')), Trapezoid(Point('Q'),Point('R'),Point('S'),Point('T')), Trapezoid(Point('J'),Point('K'),Point('L'),Point('M')), Trapezoid(Point('Q'),Point('R'),Point('S'),Point('T')),]
goal = Variable('x')
solution = '1'

diagrammatic_relations = [NotCollinear(Point('J'),Point('L'),Point('M')), SameSide(Point('L'),Point('M'),Point('J'),Point('K')), OppositeSide(Point('J'),Point('L'),Point('K'),Point('M')), NotCollinear(Point('J'),Point('K'),Point('L')), SameSide(Point('J'),Point('K'),Point('L'),Point('M')), OppositeSide(Point('K'),Point('M'),Point('J'),Point('L')), SameSide(Point('K'),Point('L'),Point('J'),Point('M')), NotCollinear(Point('J'),Point('K'),Point('M')), NotCollinear(Point('K'),Point('L'),Point('M')), SameSide(Point('J'),Point('M'),Point('K'),Point('L'))]

new_diagrammatic_relations = {SameSide(Point('J'),Point('K'),Point('L'),Point('M')), NotCollinear(Point('J'),Point('L'),Point('M')), OppositeSide(Point('K'),Point('M'),Point('J'),Point('L')), OppositeSide(Point('J'),Point('L'),Point('K'),Point('M')), SameSide(Point('J'),Point('M'),Point('K'),Point('L')), NotCollinear(Point('J'),Point('K'),Point('M')), SameSide(Point('L'),Point('M'),Point('J'),Point('K')), NotCollinear(Point('K'),Point('L'),Point('M')), SameSide(Point('K'),Point('L'),Point('J'),Point('M')), NotCollinear(Point('J'),Point('K'),Point('L'))}

