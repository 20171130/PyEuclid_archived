import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('J'),Point('L')) - ((sympy.simplify('9') * Variable('x')) - sympy.simplify('5'))), (Length(Point('J'),Point('K')) - ((sympy.simplify('6') * Variable('x')) + sympy.simplify('7'))), Between(Point('N'),Point('K'),Point('L')), Collinear(Point('K'),Point('L'),Point('N')), (Length(Point('K'),Point('N')) - Length(Point('L'),Point('N'))), Perpendicular(Point('J'),Point('N'),Point('L'),Point('N'))]
goal = Length(Point('J'),Point('K'))
solution = '31'

diagrammatic_relations = [OppositeSide(Point('K'),Point('L'),Point('J'),Point('N')), NotCollinear(Point('J'),Point('K'),Point('L')), NotCollinear(Point('J'),Point('K'),Point('N')), NotCollinear(Point('J'),Point('L'),Point('N')), SameSide(Point('L'),Point('N'),Point('J'),Point('K')), SameSide(Point('K'),Point('N'),Point('J'),Point('L'))]

new_diagrammatic_relations = {SameSide(Point('L'),Point('N'),Point('J'),Point('K')), NotCollinear(Point('J'),Point('L'),Point('N')), NotCollinear(Point('J'),Point('K'),Point('N')), SameSide(Point('K'),Point('N'),Point('J'),Point('L')), OppositeSide(Point('K'),Point('L'),Point('J'),Point('N')), Between(Point('N'),Point('K'),Point('L')), NotCollinear(Point('J'),Point('K'),Point('L'))}

