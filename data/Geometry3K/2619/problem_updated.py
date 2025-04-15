import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [Between(Point('K'),Point('F'),Point('H')), Collinear(Point('F'),Point('H'),Point('K')), Between(Point('K'),Point('E'),Point('G')), Collinear(Point('E'),Point('G'),Point('K')), Perpendicular(Point('E'),Point('H'),Point('G'),Point('H')), Rectangle(Point('E'),Point('F'),Point('G'),Point('H')), (Length(Point('F'),Point('K')) - sympy.simplify('32')), Rectangle(Point('E'),Point('F'),Point('G'),Point('H')), (Length(Point('F'),Point('K')) - sympy.simplify('32'))]
goal = Length(Point('E'),Point('G'))
solution = '64'

diagrammatic_relations = {OppositeSide(Point('E'),Point('G'),Point('F'),Point('K')), NotCollinear(Point('G'),Point('H'),Point('K')), SameSide(Point('E'),Point('F'),Point('G'),Point('H')), SameSide(Point('H'),Point('K'),Point('E'),Point('F')), SameSide(Point('E'),Point('H'),Point('F'),Point('G')), SameSide(Point('H'),Point('K'),Point('F'),Point('G')), SameSide(Point('G'),Point('H'),Point('E'),Point('F')), OppositeSide(Point('E'),Point('G'),Point('H'),Point('K')), NotCollinear(Point('E'),Point('G'),Point('H')), SameSide(Point('F'),Point('K'),Point('G'),Point('H')), SameSide(Point('G'),Point('K'),Point('E'),Point('F')), NotCollinear(Point('E'),Point('H'),Point('K')), NotCollinear(Point('E'),Point('F'),Point('G')), SameSide(Point('E'),Point('K'),Point('G'),Point('H')), SameSide(Point('G'),Point('K'),Point('E'),Point('H')), OppositeSide(Point('F'),Point('H'),Point('E'),Point('K')), SameSide(Point('F'),Point('G'),Point('E'),Point('H')), Between(Point('K'),Point('E'),Point('G')), NotCollinear(Point('F'),Point('G'),Point('K')), OppositeSide(Point('F'),Point('H'),Point('E'),Point('G')), NotCollinear(Point('E'),Point('F'),Point('H')), NotCollinear(Point('F'),Point('G'),Point('H')), OppositeSide(Point('F'),Point('H'),Point('G'),Point('K')), SameSide(Point('E'),Point('K'),Point('F'),Point('G')), NotCollinear(Point('E'),Point('F'),Point('K')), OppositeSide(Point('E'),Point('G'),Point('F'),Point('H')), SameSide(Point('F'),Point('K'),Point('E'),Point('H')), Between(Point('K'),Point('F'),Point('H'))}
