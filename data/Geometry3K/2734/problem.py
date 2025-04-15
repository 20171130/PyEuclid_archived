import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Angle(Point('A'),Point('D'),Point('C')) - ((Variable('x') / sympy.simplify('180')) * sympy.simplify('pi'))), Between(Point('D'),Point('A'),Point('B')), Collinear(Point('A'),Point('B'),Point('D')), (Angle(Point('B'),Point('D'),Point('C')) - Angle(Point('A'),Point('B'),Point('C'))), (Angle(Point('B'),Point('D'),Point('C')) - Angle(Point('B'),Point('C'),Point('D')))]
goal = Variable('x')
solution = '120'

diagrammatic_relations = [OppositeSide(Point('A'),Point('B'),Point('C'),Point('D')), NotCollinear(Point('A'),Point('C'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('C')), SameSide(Point('A'),Point('D'),Point('B'),Point('C')), NotCollinear(Point('B'),Point('C'),Point('D')), SameSide(Point('B'),Point('D'),Point('A'),Point('C'))]

new_diagrammatic_relations = {Between(Point('D'),Point('A'),Point('B')), SameSide(Point('B'),Point('D'),Point('A'),Point('C')), NotCollinear(Point('B'),Point('C'),Point('D')), OppositeSide(Point('A'),Point('B'),Point('C'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('C')), SameSide(Point('A'),Point('D'),Point('B'),Point('C')), NotCollinear(Point('A'),Point('C'),Point('D'))}

