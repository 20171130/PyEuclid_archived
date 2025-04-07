import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


relations = [(Angle(Point('F'),Point('D'),Point('G')) - Variable('angle_2')), (Angle(Point('D'),Point('E'),Point('F')) - sympy.simplify('25/180*pi')), (Angle(Point('E'),Point('D'),Point('G')) - Variable('angle_1')), (Angle(Point('D'),Point('F'),Point('E')) - sympy.simplify('65/180*pi')), Between(Point('G'),Point('E'),Point('F')), Collinear(Point('E'),Point('F'),Point('G')), Perpendicular(Point('D'),Point('G'),Point('E'),Point('G'))]
goal = Variable('angle_1')
solution = '(65)/180*pi'

diagrammatic_relations = {NotCollinear(Point('D'),Point('E'),Point('F')), OppositeSide(Point('E'),Point('F'),Point('D'),Point('G')), SameSide(Point('E'),Point('G'),Point('D'),Point('F')), SameSide(Point('F'),Point('G'),Point('D'),Point('E')), NotCollinear(Point('D'),Point('F'),Point('G')), NotCollinear(Point('D'),Point('E'),Point('G'))}
