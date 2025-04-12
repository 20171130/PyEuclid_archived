import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Angle(Point('B'),Point('A'),Point('C')) - sympy.simplify('55/180*pi')), (Length(Point('A'),Point('B')) - sympy.simplify('73')), (Angle(Point('A'),Point('B'),Point('C')) - sympy.simplify('60/180*pi')), (Length(Point('A'),Point('C')) - Variable('x'))]
goal = Variable('x')
solution = '69.8'

diagrammatic_relations = {NotCollinear(Point('A'),Point('B'),Point('C'))}
