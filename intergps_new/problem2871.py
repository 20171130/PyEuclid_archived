import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


relations = [(Length(Point('C'),Point('D')) - sympy.simplify('21')), (Length(Point('A'),Point('B')) - sympy.simplify('32')), (Length(Point('B'),Point('D')) - Length(Point('B'),Point('C'))), (Length(Point('A'),Point('D')) - Length(Point('A'),Point('C'))), Quadrilateral(Point('A'),Point('C'),Point('B'),Point('D')), Quadrilateral(Point('A'),Point('C'),Point('B'),Point('D'))]
goal = Area(Point('A'),Point('C'),Point('B'),Point('D'))
solution = '336'

diagrammatic_relations = {OppositeSide(Point('A'),Point('B'),Point('C'),Point('D')), NotCollinear(Point('A'),Point('C'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('C')), SameSide(Point('A'),Point('D'),Point('B'),Point('C')), NotCollinear(Point('A'),Point('B'),Point('D')), NotCollinear(Point('B'),Point('C'),Point('D')), OppositeSide(Point('C'),Point('D'),Point('A'),Point('B')), SameSide(Point('A'),Point('C'),Point('B'),Point('D')), SameSide(Point('B'),Point('C'),Point('A'),Point('D')), SameSide(Point('B'),Point('D'),Point('A'),Point('C'))}
