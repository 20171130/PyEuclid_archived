import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('A'),Point('H')) - sympy.simplify('7')), (Length(Point('B'),Point('C')) - sympy.simplify('10.2000000000000')), Between(Point('H'),Point('B'),Point('C')), Collinear(Point('B'),Point('C'),Point('H')), Perpendicular(Point('A'),Point('H'),Point('B'),Point('C'))]
goal = Area(Point('A'),Point('B'),Point('C'))
solution = '35.7'

diagrammatic_relations = [NotCollinear(Point('A'),Point('B'),Point('C'))]
