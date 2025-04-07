import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


relations = [(Angle(Point('A'),Point('D'),Point('C')) - sympy.simplify('38/180*pi')), (Angle(Point('C'),Point('B'),Point('D')) - Variable('angle_1')), (Angle(Point('A'),Point('C'),Point('B')) - Variable('angle_3')), (Angle(Point('A'),Point('B'),Point('C')) - sympy.simplify('72/180*pi')), (Angle(Point('C'),Point('A'),Point('D')) - sympy.simplify('42/180*pi')), (Angle(Point('B'),Point('C'),Point('D')) - Variable('angle_2')), Between(Point('B'),Point('A'),Point('D')), Collinear(Point('A'),Point('B'),Point('D'))]
goal = Variable('angle_3')
solution = '(66)/180*pi'

diagrammatic_relations = {SameSide(Point('A'),Point('B'),Point('C'),Point('D')), NotCollinear(Point('A'),Point('C'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('C')), OppositeSide(Point('A'),Point('D'),Point('B'),Point('C')), NotCollinear(Point('B'),Point('C'),Point('D')), SameSide(Point('B'),Point('D'),Point('A'),Point('C'))}
