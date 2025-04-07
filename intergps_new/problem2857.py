import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


relations = [(Length(Point('A'),Point('H')) - sympy.simplify('15')), (Length(Point('A'),Point('G')) - sympy.simplify('12')), Between(Point('A'),Point('F'),Point('H')), Collinear(Point('A'),Point('F'),Point('H')), Between(Point('A'),Point('G'),Point('J')), Collinear(Point('A'),Point('G'),Point('J')), (Length(Point('F'),Point('G')) - Length(Point('F'),Point('J'))), (Length(Point('G'),Point('H')) - Length(Point('H'),Point('J'))), Quadrilateral(Point('F'),Point('G'),Point('H'),Point('J')), Kite(Point('H'),Point('G'),Point('F'),Point('J'))]
goal = Length(Point('G'),Point('H'))
solution = 'sqrt(369)'

diagrammatic_relations = {OppositeSide(Point('F'),Point('H'),Point('G'),Point('J')), NotCollinear(Point('F'),Point('G'),Point('J')), SameSide(Point('F'),Point('J'),Point('G'),Point('H')), SameSide(Point('A'),Point('F'),Point('H'),Point('J')), NotCollinear(Point('A'),Point('F'),Point('J')), SameSide(Point('H'),Point('J'),Point('F'),Point('G')), OppositeSide(Point('F'),Point('H'),Point('A'),Point('J')), NotCollinear(Point('A'),Point('F'),Point('G')), SameSide(Point('A'),Point('J'),Point('F'),Point('G')), OppositeSide(Point('G'),Point('J'),Point('F'),Point('H')), SameSide(Point('F'),Point('G'),Point('H'),Point('J')), NotCollinear(Point('G'),Point('H'),Point('J')), SameSide(Point('A'),Point('H'),Point('F'),Point('J')), SameSide(Point('A'),Point('G'),Point('F'),Point('J')), SameSide(Point('A'),Point('F'),Point('G'),Point('H')), NotCollinear(Point('F'),Point('H'),Point('J')), NotCollinear(Point('A'),Point('H'),Point('J')), SameSide(Point('A'),Point('H'),Point('F'),Point('G')), SameSide(Point('G'),Point('H'),Point('F'),Point('J')), OppositeSide(Point('G'),Point('J'),Point('A'),Point('F')), SameSide(Point('A'),Point('J'),Point('G'),Point('H')), OppositeSide(Point('G'),Point('J'),Point('A'),Point('H')), NotCollinear(Point('A'),Point('G'),Point('H')), NotCollinear(Point('F'),Point('G'),Point('H')), SameSide(Point('A'),Point('G'),Point('H'),Point('J')), OppositeSide(Point('F'),Point('H'),Point('A'),Point('G'))}
