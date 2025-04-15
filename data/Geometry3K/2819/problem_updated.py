import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('B'),Point('C')) - sympy.simplify('17')), (Length(Point('D'),Point('E')) - sympy.simplify('8')), (Length(Point('D'),Point('E')) - Length(Point('A'),Point('E'))), Between(Point('E'),Point('B'),Point('C')), Collinear(Point('B'),Point('C'),Point('E')), Between(Point('E'),Point('A'),Point('D')), Collinear(Point('A'),Point('D'),Point('E')), Rhombus(Point('A'),Point('B'),Point('D'),Point('C'))]
goal = Area(Point('A'),Point('B'),Point('D'),Point('C'))
solution = '136'

diagrammatic_relations = {OppositeSide(Point('A'),Point('D'),Point('B'),Point('C')), NotCollinear(Point('B'),Point('C'),Point('D')), SameSide(Point('D'),Point('E'),Point('A'),Point('C')), OppositeSide(Point('B'),Point('C'),Point('D'),Point('E')), Between(Point('E'),Point('B'),Point('C')), NotCollinear(Point('B'),Point('D'),Point('E')), OppositeSide(Point('A'),Point('D'),Point('C'),Point('E')), SameSide(Point('B'),Point('D'),Point('A'),Point('C')), NotCollinear(Point('C'),Point('D'),Point('E')), SameSide(Point('C'),Point('D'),Point('A'),Point('B')), SameSide(Point('A'),Point('C'),Point('B'),Point('D')), SameSide(Point('A'),Point('B'),Point('C'),Point('D')), SameSide(Point('B'),Point('E'),Point('C'),Point('D')), OppositeSide(Point('B'),Point('C'),Point('A'),Point('D')), SameSide(Point('D'),Point('E'),Point('A'),Point('B')), SameSide(Point('C'),Point('E'),Point('A'),Point('B')), SameSide(Point('A'),Point('E'),Point('C'),Point('D')), NotCollinear(Point('A'),Point('C'),Point('E')), OppositeSide(Point('B'),Point('C'),Point('A'),Point('E')), NotCollinear(Point('A'),Point('C'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('E')), Between(Point('E'),Point('A'),Point('D')), SameSide(Point('A'),Point('E'),Point('B'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('C')), OppositeSide(Point('A'),Point('D'),Point('B'),Point('E')), SameSide(Point('B'),Point('E'),Point('A'),Point('C')), SameSide(Point('C'),Point('E'),Point('B'),Point('D'))}
