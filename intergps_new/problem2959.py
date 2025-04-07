import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


relations = [(Length(Point('A'),Point('E')) - sympy.simplify('12')), (Length(Point('D'),Point('E')) - sympy.simplify('11')), (Length(Point('D'),Point('E')) - Length(Point('C'),Point('E'))), (Length(Point('A'),Point('E')) - Length(Point('B'),Point('E'))), Between(Point('E'),Point('C'),Point('D')), Collinear(Point('C'),Point('D'),Point('E')), Between(Point('E'),Point('A'),Point('B')), Collinear(Point('A'),Point('B'),Point('E')), Rhombus(Point('A'),Point('C'),Point('B'),Point('D'))]
goal = Area(Point('A'),Point('C'),Point('B'),Point('D'))
solution = '264'

diagrammatic_relations = {Between(Point('E'),Point('C'),Point('D')), SameSide(Point('A'),Point('C'),Point('B'),Point('D')), SameSide(Point('B'),Point('E'),Point('A'),Point('D')), OppositeSide(Point('A'),Point('B'),Point('C'),Point('D')), SameSide(Point('A'),Point('D'),Point('B'),Point('C')), NotCollinear(Point('A'),Point('C'),Point('E')), OppositeSide(Point('C'),Point('D'),Point('A'),Point('B')), SameSide(Point('D'),Point('E'),Point('B'),Point('C')), SameSide(Point('A'),Point('E'),Point('B'),Point('C')), SameSide(Point('C'),Point('E'),Point('B'),Point('D')), SameSide(Point('A'),Point('E'),Point('B'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('D')), NotCollinear(Point('B'),Point('C'),Point('E')), SameSide(Point('B'),Point('C'),Point('A'),Point('D')), SameSide(Point('B'),Point('E'),Point('A'),Point('C')), SameSide(Point('D'),Point('E'),Point('A'),Point('C')), OppositeSide(Point('C'),Point('D'),Point('A'),Point('E')), NotCollinear(Point('A'),Point('C'),Point('D')), SameSide(Point('C'),Point('E'),Point('A'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('C')), OppositeSide(Point('A'),Point('B'),Point('C'),Point('E')), OppositeSide(Point('C'),Point('D'),Point('B'),Point('E')), NotCollinear(Point('A'),Point('D'),Point('E')), OppositeSide(Point('A'),Point('B'),Point('D'),Point('E')), NotCollinear(Point('B'),Point('D'),Point('E')), NotCollinear(Point('B'),Point('C'),Point('D')), SameSide(Point('B'),Point('D'),Point('A'),Point('C'))}
