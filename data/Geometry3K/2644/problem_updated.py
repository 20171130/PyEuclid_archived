import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('D'),Point('E')) - sympy.simplify('5')), (Length(Point('C'),Point('E')) - sympy.simplify('12')), Between(Point('E'),Point('A'),Point('C')), Collinear(Point('A'),Point('C'),Point('E')), Between(Point('E'),Point('B'),Point('D')), Collinear(Point('B'),Point('D'),Point('E')), (Length(Point('A'),Point('B')) - Length(Point('A'),Point('D'))), (Length(Point('B'),Point('C')) - Length(Point('C'),Point('D'))), Perpendicular(Point('A'),Point('E'),Point('D'),Point('E'))]
goal = Length(Point('B'),Point('C'))
solution = '13'

diagrammatic_relations = {NotCollinear(Point('A'),Point('D'),Point('E')), NotCollinear(Point('B'),Point('C'),Point('D')), Between(Point('E'),Point('A'),Point('C')), NotCollinear(Point('B'),Point('C'),Point('E')), OppositeSide(Point('B'),Point('D'),Point('A'),Point('C')), NotCollinear(Point('C'),Point('D'),Point('E')), SameSide(Point('C'),Point('D'),Point('A'),Point('B')), OppositeSide(Point('B'),Point('D'),Point('C'),Point('E')), Between(Point('E'),Point('B'),Point('D')), SameSide(Point('A'),Point('D'),Point('B'),Point('C')), SameSide(Point('A'),Point('B'),Point('C'),Point('D')), OppositeSide(Point('A'),Point('C'),Point('B'),Point('E')), SameSide(Point('B'),Point('E'),Point('A'),Point('D')), SameSide(Point('B'),Point('E'),Point('C'),Point('D')), SameSide(Point('D'),Point('E'),Point('A'),Point('B')), SameSide(Point('C'),Point('E'),Point('A'),Point('B')), SameSide(Point('A'),Point('E'),Point('C'),Point('D')), SameSide(Point('A'),Point('E'),Point('B'),Point('C')), NotCollinear(Point('A'),Point('C'),Point('D')), SameSide(Point('B'),Point('C'),Point('A'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('D')), OppositeSide(Point('A'),Point('C'),Point('B'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('E')), OppositeSide(Point('B'),Point('D'),Point('A'),Point('E')), NotCollinear(Point('A'),Point('B'),Point('C')), SameSide(Point('C'),Point('E'),Point('A'),Point('D')), OppositeSide(Point('A'),Point('C'),Point('D'),Point('E')), SameSide(Point('D'),Point('E'),Point('B'),Point('C'))}
