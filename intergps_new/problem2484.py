import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


relations = [(Length(Point('A'),Point('B')) - sympy.simplify('42')), (Length(Point('B'),Point('C')) - sympy.simplify('38')), (Length(Point('A'),Point('C')) - Variable('x')), Perpendicular(Point('A'),Point('C'),Point('B'),Point('C'))]
goal = Variable('x')
solution = '8*sqrt(5)'

diagrammatic_relations = {NotCollinear(Point('A'),Point('B'),Point('C'))}
