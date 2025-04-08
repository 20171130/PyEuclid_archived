import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('C'),Point('D')) - sympy.simplify('8')), (Length(Point('A'),Point('D')) - ((sympy.simplify('6') * Variable('x')) + sympy.simplify('2'))), (Length(Point('B'),Point('C')) - sympy.simplify('10')), (Length(Point('A'),Point('B')) - ((sympy.simplify('9') * Variable('x')) - sympy.simplify('2'))), Between(Point('D'),Point('A'),Point('C')), Collinear(Point('A'),Point('C'),Point('D')), (Angle(Point('C'),Point('B'),Point('D')) - Angle(Point('A'),Point('B'),Point('D')))]
goal = Variable('x')
solution = '3'

diagrammatic_relations = [NotCollinear(Point('A'),Point('B'),Point('C')), SameSide(Point('A'),Point('D'),Point('B'),Point('C')), NotCollinear(Point('A'),Point('B'),Point('D')), SameSide(Point('C'),Point('D'),Point('A'),Point('B')), OppositeSide(Point('A'),Point('C'),Point('B'),Point('D')), NotCollinear(Point('B'),Point('C'),Point('D'))]
