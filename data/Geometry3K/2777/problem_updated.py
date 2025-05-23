import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('B'),Point('F')) - Variable('x')), (Length(Point('A'),Point('B')) - Variable('y')), (Length(Point('A'),Point('F')) - Variable('z')), (Length(Point('F'),Point('L')) - (sympy.simplify('2') * sympy.sqrt(sympy.simplify('3')))), (Length(Point('A'),Point('L')) - sympy.sqrt(sympy.simplify('3'))), Between(Point('B'),Point('F'),Point('L')), Collinear(Point('B'),Point('F'),Point('L')), Perpendicular(Point('A'),Point('B'),Point('B'),Point('F')), Perpendicular(Point('A'),Point('F'),Point('A'),Point('L'))]
goal = Variable('z')
solution = '3'

diagrammatic_relations = {SameSide(Point('B'),Point('L'),Point('A'),Point('F')), SameSide(Point('B'),Point('F'),Point('A'),Point('L')), NotCollinear(Point('A'),Point('B'),Point('F')), NotCollinear(Point('A'),Point('F'),Point('L')), OppositeSide(Point('F'),Point('L'),Point('A'),Point('B')), Between(Point('B'),Point('F'),Point('L')), NotCollinear(Point('A'),Point('B'),Point('L'))}
