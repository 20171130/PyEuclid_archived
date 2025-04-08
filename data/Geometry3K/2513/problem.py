import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('B'),Point('C')) - sympy.simplify('16')), (Angle(Point('B'),Point('A'),Point('C')) - sympy.simplify('97/180*pi')), (Angle(Point('A'),Point('C'),Point('B')) - sympy.simplify('21/180*pi')), (Length(Point('A'),Point('B')) - Variable('x'))]
goal = Variable('x')
solution = '5.8'

diagrammatic_relations = [NotCollinear(Point('A'),Point('B'),Point('C'))]
