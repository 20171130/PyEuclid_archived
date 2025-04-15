import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Angle(Point('A'),Point('B'),Point('C')) - ((((sympy.simplify('2') * Variable('x')) + sympy.simplify('41')) / sympy.simplify('180')) * sympy.simplify('pi'))), (Angle(Point('A'),Point('D'),Point('C')) - sympy.simplify('115/180*pi')), (Length(Point('C'),Point('D')) - ((sympy.simplify('3') * Variable('y')) + sympy.simplify('13'))), (Length(Point('A'),Point('B')) - ((sympy.simplify('2') * Variable('y')) + sympy.simplify('19'))), Parallelogram(Point('A'),Point('B'),Point('C'),Point('D'))]
goal = Variable('x')
solution = '37'

diagrammatic_relations = [SameSide(Point('A'),Point('B'),Point('C'),Point('D')), NotCollinear(Point('A'),Point('C'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('C')), SameSide(Point('A'),Point('D'),Point('B'),Point('C')), NotCollinear(Point('A'),Point('B'),Point('D')), SameSide(Point('C'),Point('D'),Point('A'),Point('B')), OppositeSide(Point('A'),Point('C'),Point('B'),Point('D')), SameSide(Point('B'),Point('C'),Point('A'),Point('D')), NotCollinear(Point('B'),Point('C'),Point('D')), OppositeSide(Point('B'),Point('D'),Point('A'),Point('C'))]

new_diagrammatic_relations = {SameSide(Point('C'),Point('D'),Point('A'),Point('B')), SameSide(Point('B'),Point('C'),Point('A'),Point('D')), NotCollinear(Point('B'),Point('C'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('D')), OppositeSide(Point('A'),Point('C'),Point('B'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('C')), SameSide(Point('A'),Point('B'),Point('C'),Point('D')), SameSide(Point('A'),Point('D'),Point('B'),Point('C')), OppositeSide(Point('B'),Point('D'),Point('A'),Point('C')), NotCollinear(Point('A'),Point('C'),Point('D'))}

