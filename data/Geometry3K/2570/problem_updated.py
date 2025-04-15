import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('K'),Point('L')) - sympy.simplify('17')), (Length(Point('A'),Point('L')) - sympy.simplify('10')), (Length(Point('A'),Point('M')) - Variable('x')), (Length(Point('K'),Point('M')) - Variable('x')), Between(Point('A'),Point('L'),Point('M')), Collinear(Point('A'),Point('L'),Point('M')), Perpendicular(Point('K'),Point('L'),Point('K'),Point('M')), (Length(Point('K'),Point('M')) - Variable('radius_M')), (Length(Point('A'),Point('M')) - Variable('radius_M')), (Angle(Point('L'),Point('K'),Point('M')) - sympy.simplify('pi/2')), (Angle(Point('L'),Point('K'),Point('M')) - sympy.simplify('pi/2'))]
goal = Variable('x')
solution = '9.45'

diagrammatic_relations = {Between(Point('A'),Point('L'),Point('M')), NotCollinear(Point('A'),Point('K'),Point('L')), NotCollinear(Point('A'),Point('K'),Point('M')), OppositeSide(Point('L'),Point('M'),Point('A'),Point('K')), SameSide(Point('A'),Point('M'),Point('K'),Point('L')), NotCollinear(Point('K'),Point('L'),Point('M')), SameSide(Point('A'),Point('L'),Point('K'),Point('M'))}
