import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('A'),Point('C')) - ((sympy.simplify('2') * Variable('x')) - sympy.simplify('5'))), (Length(Point('A'),Point('D')) - (sympy.simplify('5') * Variable('y'))), (Length(Point('B'),Point('D')) - ((sympy.simplify('3') * Variable('x')) - sympy.simplify('18'))), (Length(Point('B'),Point('C')) - ((sympy.simplify('2') * Variable('y')) + sympy.simplify('12'))), Parallelogram(Point('A'),Point('C'),Point('B'),Point('D'))]
goal = Variable('x')
solution = '13'

diagrammatic_relations = {SameSide(Point('B'),Point('D'),Point('A'),Point('C')), SameSide(Point('B'),Point('C'),Point('A'),Point('D')), NotCollinear(Point('B'),Point('C'),Point('D')), OppositeSide(Point('C'),Point('D'),Point('A'),Point('B')), OppositeSide(Point('A'),Point('B'),Point('C'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('C')), SameSide(Point('A'),Point('C'),Point('B'),Point('D')), SameSide(Point('A'),Point('D'),Point('B'),Point('C')), NotCollinear(Point('A'),Point('C'),Point('D'))}
