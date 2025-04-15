import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('A'),Point('C')) - sympy.simplify('3.20000000000000')), (Length(Point('A'),Point('C')) - Length(Point('A'),Point('B'))), (Length(Point('A'),Point('B')) - Length(Point('C'),Point('D'))), (Length(Point('C'),Point('D')) - Length(Point('B'),Point('D'))), Perpendicular(Point('A'),Point('C'),Point('C'),Point('D')), Square(Point('A'),Point('B'),Point('D'),Point('C'))]
goal = Area(Point('A'),Point('B'),Point('D'),Point('C'))
solution = '10.2'

diagrammatic_relations = {SameSide(Point('B'),Point('D'),Point('A'),Point('C')), SameSide(Point('C'),Point('D'),Point('A'),Point('B')), OppositeSide(Point('A'),Point('D'),Point('B'),Point('C')), NotCollinear(Point('B'),Point('C'),Point('D')), OppositeSide(Point('B'),Point('C'),Point('A'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('C')), SameSide(Point('A'),Point('C'),Point('B'),Point('D')), SameSide(Point('A'),Point('B'),Point('C'),Point('D')), NotCollinear(Point('A'),Point('C'),Point('D'))}
