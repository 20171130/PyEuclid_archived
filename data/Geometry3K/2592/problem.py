import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('B'),Point('C')) - sympy.simplify('6')), (Length(Point('B'),Point('A')) - sympy.simplify('6')), (Angle(Point('A'),Point('B'),Point('C')) - sympy.simplify('120/180*pi'))]
goal = Length(Point('B'),Point('C')) ** 2 * sympy.simplify('pi') / 3 - Area(Point('A'),Point('B'),Point('C'))
solution = '22.1'

diagrammatic_relations = [NotCollinear(Point('A'),Point('B'),Point('C'))]

new_diagrammatic_relations = {NotCollinear(Point('A'),Point('B'),Point('C'))}

