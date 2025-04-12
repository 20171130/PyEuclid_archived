import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('C'),Point('D')) - sympy.simplify('8')), (Length(Point('A'),Point('D')) - ((sympy.simplify('6') * Variable('x')) + sympy.simplify('2'))), (Length(Point('B'),Point('C')) - sympy.simplify('10')), (Length(Point('A'),Point('B')) - ((sympy.simplify('9') * Variable('x')) - sympy.simplify('2'))), Between(Point('D'),Point('A'),Point('C')), Collinear(Point('A'),Point('C'),Point('D')), (Angle(Point('C'),Point('B'),Point('D')) - Angle(Point('A'),Point('B'),Point('D')))]
goal = Variable('x')
solution = '3'

diagrammatic_relations = {SameSide(Point('C'),Point('D'),Point('A'),Point('B')), NotCollinear(Point('B'),Point('C'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('D')), OppositeSide(Point('A'),Point('C'),Point('B'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('C')), SameSide(Point('A'),Point('D'),Point('B'),Point('C')), Between(Point('D'),Point('A'),Point('C'))}
