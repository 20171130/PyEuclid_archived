import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('F'),Point('G')) - sympy.simplify('16')), (Length(Point('F'),Point('H')) - sympy.simplify('12')), Between(Point('H'),Point('F'),Point('G')), Collinear(Point('F'),Point('G'),Point('H')), Perpendicular(Point('E'),Point('H'),Point('F'),Point('H')), Perpendicular(Point('E'),Point('F'),Point('E'),Point('G'))]
goal = Length(Point('E'),Point('H'))
solution = '4*sqrt(3)'

diagrammatic_relations = {NotCollinear(Point('E'),Point('G'),Point('H')), Between(Point('H'),Point('F'),Point('G')), NotCollinear(Point('E'),Point('F'),Point('H')), NotCollinear(Point('E'),Point('F'),Point('G')), SameSide(Point('F'),Point('H'),Point('E'),Point('G')), OppositeSide(Point('F'),Point('G'),Point('E'),Point('H')), SameSide(Point('G'),Point('H'),Point('E'),Point('F'))}
