import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('A'),Point('B')) - sympy.simplify('3')), (Angle(Point('A'),Point('N'),Point('B')) - sympy.simplify('62/180*pi')), (Length(Point('A'),Point('B')) - Length(Point('D'),Point('N'))), (Length(Point('A'),Point('D')) - Length(Point('B'),Point('N'))), Perpendicular(Point('A'),Point('D'),Point('D'),Point('N')), Perpendicular(Point('A'),Point('B'),Point('B'),Point('N')), Rectangle(Point('A'),Point('B'),Point('N'),Point('D'))]
goal = Area(Point('A'),Point('B'),Point('N'),Point('D'))
solution = '4.8'

diagrammatic_relations = [OppositeSide(Point('B'),Point('D'),Point('A'),Point('N')), NotCollinear(Point('B'),Point('D'),Point('N')), SameSide(Point('D'),Point('N'),Point('A'),Point('B')), NotCollinear(Point('A'),Point('B'),Point('N')), SameSide(Point('A'),Point('B'),Point('D'),Point('N')), OppositeSide(Point('A'),Point('N'),Point('B'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('D')), SameSide(Point('B'),Point('N'),Point('A'),Point('D')), SameSide(Point('A'),Point('D'),Point('B'),Point('N')), NotCollinear(Point('A'),Point('D'),Point('N'))]
