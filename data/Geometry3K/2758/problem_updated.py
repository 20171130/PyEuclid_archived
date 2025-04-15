import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('J'),Point('K')) - sympy.simplify('13')), (Length(Point('G'),Point('H')) - sympy.simplify('17')), (Area(Point('G'),Point('H'),Point('J'),Point('K')) - sympy.simplify('75')), Trapezoid(Point('G'),Point('H'),Point('J'),Point('K')), (Area(Point('G'),Point('H'),Point('J'),Point('K')) - sympy.simplify('75')), Trapezoid(Point('G'),Point('H'),Point('J'),Point('K')), Between(Point('A'),Point('G'),Point('H')), Collinear(Point('A'),Point('G'),Point('H')), Perpendicular(Point('A'),Point('J'),Point('G'),Point('H'))]
goal = Length(Point('A'),Point('J'))
solution = '5'

diagrammatic_relations = {SameSide(Point('H'),Point('J'),Point('G'),Point('K')), NotCollinear(Point('G'),Point('H'),Point('K')), NotCollinear(Point('H'),Point('J'),Point('K')), NotCollinear(Point('G'),Point('H'),Point('J')), NotCollinear(Point('G'),Point('J'),Point('K')), OppositeSide(Point('G'),Point('J'),Point('H'),Point('K')), SameSide(Point('J'),Point('K'),Point('G'),Point('H')), SameSide(Point('G'),Point('H'),Point('J'),Point('K')), SameSide(Point('G'),Point('K'),Point('H'),Point('J')), OppositeSide(Point('H'),Point('K'),Point('G'),Point('J'))}
