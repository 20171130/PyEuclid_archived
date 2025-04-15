import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Angle(Point('B'),Point('C'),Point('D')) - Variable('angle_2')), (Angle(Point('A'),Point('C'),Point('B')) - Variable('angle_1')), Between(Point('C'),Point('A'),Point('D')), Collinear(Point('A'),Point('C'),Point('D')),  (Variable('angle_2') - sympy.simplify('67/180*pi')), ((Variable('angle_1') + Variable('angle_2')) - sympy.simplify('pi')), (Variable('angle_2') - sympy.simplify('67/180*pi'))]
goal = Variable('angle_1')
solution = '(113)/180*pi'

diagrammatic_relations = {SameSide(Point('C'),Point('D'),Point('A'),Point('B')), OppositeSide(Point('A'),Point('D'),Point('B'),Point('C')), NotCollinear(Point('B'),Point('C'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('D')), Between(Point('C'),Point('A'),Point('D')), SameSide(Point('A'),Point('C'),Point('B'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('C'))}
