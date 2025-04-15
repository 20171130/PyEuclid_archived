import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Similar4P(Point('A'),Point('C'),Point('B'),Point('D'),Point('E'),Point('F'),Point('G'),Point('H'))) , (Length(Point('B'),Point('C')) - 40), (Length(Point('F'),Point('G')) - Variable('x')), (Area(Point('A'),Point('C'),Point('B'),Point('D')) - 400), Quadrilateral(Point('A'),Point('C'),Point('B'),Point('D')), (Area(Point('E'),Point('F'),Point('G'),Point('H')) - 64), Quadrilateral(Point('E'),Point('F'),Point('G'),Point('H')), ]
goal = Variable('x')
solution = '16'
diagrammatic_relations = {SameSide(Point('B'),Point('D'),Point('A'),Point('C')), SameSide(Point('B'),Point('C'),Point('A'),Point('D')), NotCollinear(Point('B'),Point('C'),Point('D')), OppositeSide(Point('C'),Point('D'),Point('A'),Point('B')), OppositeSide(Point('A'),Point('B'),Point('C'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('C')), SameSide(Point('A'),Point('C'),Point('B'),Point('D')), SameSide(Point('A'),Point('D'),Point('B'),Point('C')), NotCollinear(Point('A'),Point('C'),Point('D'))}
