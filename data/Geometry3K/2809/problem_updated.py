import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [Angle(Point('A'),Point('B'),Point('C'))-sympy.simplify('3')*Angle(Point('B'),Point('A'),Point('C')), Angle(Point('A'),Point('C'),Point('B'))- sympy.simplify('2')*Angle(Point('B'),Point('A'),Point('C'))]
goal =Angle(Point('B'),Point('A'),Point('C'))
solution = '30*pi/180'

diagrammatic_relations = {NotCollinear(Point('A'),Point('B'),Point('C'))}
