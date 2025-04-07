import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


relations = [Between(Point('H'),Point('G'),Point('I')), Collinear(Point('G'),Point('H'),Point('I')), Between(Point('K'),Point('G'),Point('J')), Collinear(Point('G'),Point('J'),Point('K')), Parallel(Point('H'),Point('K'),Point('I'),Point('J')), (Length(Point('G'),Point('H')) - sympy.simplify('9')), (Length(Point('G'),Point('K')) - sympy.simplify('6')), (Length(Point('J'),Point('K')) - sympy.simplify('4')), (Length(Point('G'),Point('H')) - sympy.simplify('9')), (Length(Point('G'),Point('K')) - sympy.simplify('6')), (Length(Point('J'),Point('K')) - sympy.simplify('4'))]
goal = Length(Point('G'),Point('I'))
solution = '15'

diagrammatic_relations = {OppositeSide(Point('H'),Point('J'),Point('I'),Point('K')), SameSide(Point('G'),Point('K'),Point('H'),Point('J')), OppositeSide(Point('G'),Point('J'),Point('H'),Point('K')), OppositeSide(Point('G'),Point('J'),Point('I'),Point('K')), OppositeSide(Point('G'),Point('I'),Point('H'),Point('J')), OppositeSide(Point('G'),Point('I'),Point('H'),Point('K')), NotCollinear(Point('G'),Point('H'),Point('K')), SameSide(Point('G'),Point('H'),Point('I'),Point('J')), NotCollinear(Point('G'),Point('I'),Point('K')), SameSide(Point('J'),Point('K'),Point('G'),Point('I')), SameSide(Point('G'),Point('H'),Point('I'),Point('K')), SameSide(Point('H'),Point('K'),Point('I'),Point('J')), NotCollinear(Point('G'),Point('I'),Point('J')), SameSide(Point('I'),Point('J'),Point('H'),Point('K')), SameSide(Point('J'),Point('K'),Point('H'),Point('I')), NotCollinear(Point('G'),Point('H'),Point('J')), NotCollinear(Point('I'),Point('J'),Point('K')), OppositeSide(Point('I'),Point('K'),Point('H'),Point('J')), SameSide(Point('H'),Point('I'),Point('J'),Point('K')), SameSide(Point('G'),Point('K'),Point('I'),Point('J')), SameSide(Point('J'),Point('K'),Point('G'),Point('H')), NotCollinear(Point('H'),Point('J'),Point('K')), SameSide(Point('H'),Point('I'),Point('G'),Point('K')), NotCollinear(Point('H'),Point('I'),Point('K')), SameSide(Point('H'),Point('I'),Point('G'),Point('J')), NotCollinear(Point('H'),Point('I'),Point('J'))}
