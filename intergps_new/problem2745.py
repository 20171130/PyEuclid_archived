import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


relations = [(Length(Point('A'),Point('B')) - ((sympy.simplify('2') * Variable('y')) + sympy.simplify('1'))), (Length(Point('C'),Point('D')) - (sympy.simplify('3') - (sympy.simplify('4') * Variable('w')))), (Length(Point('A'),Point('D')) - ((sympy.simplify('3') * Variable('x')) - sympy.simplify('2'))), (Length(Point('B'),Point('C')) - ((Variable('x') - Variable('w')) + sympy.simplify('1'))), ((((Length(Point('A'),Point('B')) + Length(Point('B'),Point('C'))) + Length(Point('C'),Point('D'))) + Length(Point('A'),Point('D'))) - sympy.simplify('22')), Parallelogram(Point('A'),Point('B'),Point('C'),Point('D')), Parallelogram(Point('A'),Point('B'),Point('C'),Point('D')), ((((Length(Point('A'),Point('B')) + Length(Point('B'),Point('C'))) + Length(Point('C'),Point('D'))) + Length(Point('A'),Point('D'))) - sympy.simplify('22')), Quadrilateral(Point('A'),Point('B'),Point('C'),Point('D'))]
goal = Length(Point('A'),Point('B'))
solution = '7'

diagrammatic_relations = {SameSide(Point('A'),Point('B'),Point('C'),Point('D')), NotCollinear(Point('A'),Point('C'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('C')), SameSide(Point('A'),Point('D'),Point('B'),Point('C')), NotCollinear(Point('A'),Point('B'),Point('D')), SameSide(Point('C'),Point('D'),Point('A'),Point('B')), OppositeSide(Point('A'),Point('C'),Point('B'),Point('D')), SameSide(Point('B'),Point('C'),Point('A'),Point('D')), NotCollinear(Point('B'),Point('C'),Point('D')), OppositeSide(Point('B'),Point('D'),Point('A'),Point('C'))}
