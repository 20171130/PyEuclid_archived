import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('B'),Point('E')) - sympy.simplify('16')), (Length(Point('A'),Point('E')) - sympy.simplify('9')), Perpendicular(Point('A'),Point('E'),Point('B'),Point('E')), Perpendicular(Point('B'),Point('D'),Point('B'),Point('E')), Perpendicular(Point('A'),Point('D'),Point('B'),Point('D')), Perpendicular(Point('A'),Point('D'),Point('A'),Point('E')), Rectangle(Point('A'),Point('E'),Point('B'),Point('F'))]
goal = Area(Point('A'),Point('E'),Point('B'),Point('F'))
solution = '144'

diagrammatic_relations = [SameSide(Point('B'),Point('D'),Point('A'),Point('E')), OppositeSide(Point('D'),Point('E'),Point('A'),Point('B')), SameSide(Point('A'),Point('E'),Point('B'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('E')), NotCollinear(Point('A'),Point('B'),Point('D')), NotCollinear(Point('A'),Point('D'),Point('E')), SameSide(Point('A'),Point('D'),Point('B'),Point('E')), OppositeSide(Point('A'),Point('B'),Point('D'),Point('E')), NotCollinear(Point('B'),Point('D'),Point('E')), SameSide(Point('B'),Point('E'),Point('A'),Point('D'))]

new_diagrammatic_relations = {OppositeSide(Point('A'),Point('B'),Point('D'),Point('E')), OppositeSide(Point('D'),Point('E'),Point('A'),Point('B')), NotCollinear(Point('A'),Point('D'),Point('E')), NotCollinear(Point('A'),Point('B'),Point('D')), NotCollinear(Point('B'),Point('D'),Point('E')), NotCollinear(Point('A'),Point('B'),Point('E')), SameSide(Point('A'),Point('D'),Point('B'),Point('E')), SameSide(Point('A'),Point('E'),Point('B'),Point('D')), SameSide(Point('B'),Point('E'),Point('A'),Point('D')), SameSide(Point('B'),Point('D'),Point('A'),Point('E'))}

