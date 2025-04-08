import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('F'),Point('G')) - sympy.simplify('19')), (Angle(Point('D'),Point('G'),Point('F')) - sympy.simplify('125/180*pi')), (Length(Point('D'),Point('G')) - sympy.simplify('15')), (Length(Point('D'),Point('F')) - Variable('x'))]
goal = Variable('x')
solution = '30.2'

diagrammatic_relations = [NotCollinear(Point('D'),Point('F'),Point('G'))]
