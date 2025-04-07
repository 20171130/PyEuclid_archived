import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


relations = [(Angle(Point('A'),Point('D'),Point('B')) - Variable('angle_2')), Between(Point('C'),Point('A'),Point('B')), Collinear(Point('A'),Point('B'),Point('C')), (Length(Point('A'),Point('C')) - Variable('radius_C')), (Length(Point('B'),Point('C')) - Variable('radius_C')), (Length(Point('C'),Point('D')) - Variable('radius_C'))]
goal = Variable('angle_2')
solution = '(90)/180*pi'

diagrammatic_relations = {OppositeSide(Point('A'),Point('B'),Point('C'),Point('D')), NotCollinear(Point('A'),Point('C'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('D')), NotCollinear(Point('B'),Point('C'),Point('D')), SameSide(Point('A'),Point('C'),Point('B'),Point('D')), SameSide(Point('B'),Point('C'),Point('A'),Point('D'))}
