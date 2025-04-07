import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


relations = [(Length(Point('D'),Point('E')) - sympy.simplify('12')), (Length(Point('A'),Point('E')) - sympy.simplify('7')), (Length(Point('A'),Point('E')) - Length(Point('B'),Point('E'))), (Length(Point('C'),Point('E')) - Length(Point('D'),Point('E'))), Between(Point('E'),Point('C'),Point('D')), Collinear(Point('C'),Point('D'),Point('E')), Between(Point('E'),Point('A'),Point('B')), Collinear(Point('A'),Point('B'),Point('E')), Rhombus(Point('A'),Point('C'),Point('B'),Point('D'))]
goal = Area(Point('A'),Point('C'),Point('B'),Point('D'))
solution = '168'

diagrammatic_relations = {OppositeSide(Point('A'),Point('B'),Point('C'),Point('D')), NotCollinear(Point('A'),Point('C'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('C')), SameSide(Point('A'),Point('D'),Point('B'),Point('C')), NotCollinear(Point('A'),Point('B'),Point('D')), NotCollinear(Point('B'),Point('C'),Point('D')), OppositeSide(Point('C'),Point('D'),Point('A'),Point('B')), SameSide(Point('A'),Point('C'),Point('B'),Point('D')), SameSide(Point('B'),Point('C'),Point('A'),Point('D')), SameSide(Point('B'),Point('D'),Point('A'),Point('C'))}
