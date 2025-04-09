import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('A'),Point('C')) - sympy.simplify('10')), (Length(Point('B'),Point('C')) - sympy.simplify('18')), (Length(Point('A'),Point('B')) - sympy.simplify('14')), (Length(Point('B'),Point('D')) - Variable('x')), Between(Point('D'),Point('B'),Point('C')), Collinear(Point('B'),Point('C'),Point('D')), (Angle(Point('B'),Point('A'),Point('D')) - Angle(Point('C'),Point('A'),Point('D')))]
goal = Variable('x')
solution = '10.5'

diagrammatic_relations = [NotCollinear(Point('A'),Point('C'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('C')), NotCollinear(Point('A'),Point('B'),Point('D')), SameSide(Point('C'),Point('D'),Point('A'),Point('B')), OppositeSide(Point('B'),Point('C'),Point('A'),Point('D')), SameSide(Point('B'),Point('D'),Point('A'),Point('C'))]

new_diagrammatic_relations = {SameSide(Point('B'),Point('D'),Point('A'),Point('C')), SameSide(Point('C'),Point('D'),Point('A'),Point('B')), Between(Point('D'),Point('B'),Point('C')), OppositeSide(Point('B'),Point('C'),Point('A'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('C')), NotCollinear(Point('A'),Point('C'),Point('D'))}

