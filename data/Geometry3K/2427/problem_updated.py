import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('B'),Point('C')) - Variable('x')), (Length(Point('A'),Point('B')) - sympy.simplify('5')), (Length(Point('A'),Point('C')) - (sympy.simplify('3') * sympy.sqrt(sympy.simplify('2')))), Perpendicular(Point('A'),Point('C'),Point('B'),Point('C'))]
goal = Variable('x')
solution = 'sqrt(7)'

diagrammatic_relations = {NotCollinear(Point('A'),Point('B'),Point('C'))}
