import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


relations = [(Angle(Point('F'),Point('G'),Point('H')) - sympy.simplify('128/180*pi')), (Angle(Point('F'),Point('J'),Point('H')) - sympy.simplify('72/180*pi')), (Length(Point('F'),Point('G')) - Length(Point('G'),Point('H'))), (Length(Point('H'),Point('J')) - Length(Point('F'),Point('J'))), Quadrilateral(Point('F'),Point('G'),Point('H'),Point('J'))]
goal = Angle(Point('G'),Point('F'),Point('J'))
solution = '(80)/180*pi'

diagrammatic_relations = {OppositeSide(Point('F'),Point('H'),Point('G'),Point('J')), SameSide(Point('F'),Point('G'),Point('H'),Point('J')), NotCollinear(Point('G'),Point('H'),Point('J')), NotCollinear(Point('F'),Point('H'),Point('J')), SameSide(Point('H'),Point('J'),Point('F'),Point('G')), NotCollinear(Point('F'),Point('G'),Point('J')), NotCollinear(Point('F'),Point('G'),Point('H')), SameSide(Point('F'),Point('J'),Point('G'),Point('H')), SameSide(Point('G'),Point('H'),Point('F'),Point('J')), OppositeSide(Point('G'),Point('J'),Point('F'),Point('H'))}
