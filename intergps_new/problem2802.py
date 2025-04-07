import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


relations = [(Angle(Point('A'),Point('D'),Point('B')) - sympy.simplify('92/180*pi')), Between(Point('C'),Point('B'),Point('D')), Collinear(Point('B'),Point('C'),Point('D')), (Length(Point('A'),Point('C')) - Length(Point('B'),Point('C'))), (Length(Point('C'),Point('D')) - Length(Point('A'),Point('D')))]
goal = Angle(Point('C'),Point('A'),Point('D'))
solution = '(44)/180*pi'

diagrammatic_relations = {NotCollinear(Point('A'),Point('C'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('C')), NotCollinear(Point('A'),Point('B'),Point('D')), SameSide(Point('C'),Point('D'),Point('A'),Point('B')), SameSide(Point('B'),Point('C'),Point('A'),Point('D')), OppositeSide(Point('B'),Point('D'),Point('A'),Point('C'))}
