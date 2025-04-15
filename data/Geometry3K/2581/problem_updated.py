import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('C'),Point('D')) - ((sympy.simplify('3') * Variable('y')) - sympy.simplify('5'))), (Length(Point('A'),Point('B')) - (Variable('y') + sympy.simplify('11'))), (Length(Point('A'),Point('C')) - (Variable('x') + sympy.simplify('7'))), (Length(Point('B'),Point('D')) - ((sympy.simplify('2') * Variable('x')) + sympy.simplify('3'))), Parallelogram(Point('A'),Point('B'),Point('D'),Point('C'))]
goal = Variable('x')
solution = '4'

diagrammatic_relations = {SameSide(Point('B'),Point('D'),Point('A'),Point('C')), SameSide(Point('C'),Point('D'),Point('A'),Point('B')), OppositeSide(Point('A'),Point('D'),Point('B'),Point('C')), NotCollinear(Point('B'),Point('C'),Point('D')), OppositeSide(Point('B'),Point('C'),Point('A'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('C')), SameSide(Point('A'),Point('C'),Point('B'),Point('D')), SameSide(Point('A'),Point('B'),Point('C'),Point('D')), NotCollinear(Point('A'),Point('C'),Point('D'))}
