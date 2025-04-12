import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Angle(Point('B'),Point('C'),Point('D')) - sympy.simplify('54/180*pi')), (Length(Point('A'),Point('D')) - Variable('x')), (Length(Point('B'),Point('D')) - sympy.simplify('32')), (Length(Point('A'),Point('B')) - Variable('y')), Between(Point('A'),Point('C'),Point('D')), Collinear(Point('A'),Point('C'),Point('D')), (Length(Point('B'),Point('D')) - Length(Point('B'),Point('C'))), Perpendicular(Point('A'),Point('B'),Point('A'),Point('C'))]
goal = Variable('x')
solution = '18.8'

diagrammatic_relations = {NotCollinear(Point('B'),Point('C'),Point('D')), OppositeSide(Point('C'),Point('D'),Point('A'),Point('B')), NotCollinear(Point('A'),Point('B'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('C')), SameSide(Point('A'),Point('C'),Point('B'),Point('D')), SameSide(Point('A'),Point('D'),Point('B'),Point('C')), Between(Point('A'),Point('C'),Point('D'))}
