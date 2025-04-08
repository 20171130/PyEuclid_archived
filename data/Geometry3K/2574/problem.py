import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Angle(Point('G'),Point('K'),Point('H')) - sympy.simplify('122/180*pi')), Between(Point('K'),Point('G'),Point('J')), Collinear(Point('G'),Point('J'),Point('K')), Between(Point('K'),Point('G'),Point('J')), Between(Point('K'),Point('G'),Point('J')), ((Length(Point('G'),Point('J')) - Variable('radius_K')) - Variable('radius_K')), Collinear(Point('G'),Point('J'),Point('K')), ((Length(Point('G'),Point('J')) - Variable('radius_K')) - Variable('radius_K')), Collinear(Point('G'),Point('J'),Point('K')), (Length(Point('K'),Point('L')) - Variable('radius_K')), (Length(Point('H'),Point('K')) - Variable('radius_K')), (Length(Point('J'),Point('K')) - Variable('radius_K')), (Length(Point('G'),Point('K')) - Variable('radius_K'))]
goal = Angle(Point('G'),Point('K'),Point('J'))
solution = '(180)/180*pi'

diagrammatic_relations = [SameSide(Point('G'),Point('K'),Point('H'),Point('J')), OppositeSide(Point('G'),Point('J'),Point('H'),Point('K')), NotCollinear(Point('G'),Point('H'),Point('J')), SameSide(Point('J'),Point('K'),Point('G'),Point('H')), NotCollinear(Point('H'),Point('J'),Point('K')), NotCollinear(Point('G'),Point('H'),Point('K'))]
