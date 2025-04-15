import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Angle(Point('A'),Point('D'),Point('C')) - sympy.simplify('122/180*pi')), (Length(Point('B'),Point('D')) - Variable('radius_D')), (Length(Point('C'),Point('D')) - Variable('radius_D')), (Length(Point('A'),Point('D')) - Variable('radius_D'))]
goal = Angle(Point('A'),Point('B'),Point('C'))
solution = '(61)/180*pi'

diagrammatic_relations = [OppositeSide(Point('A'),Point('B'),Point('C'),Point('D')), NotCollinear(Point('A'),Point('C'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('C')), SameSide(Point('A'),Point('D'),Point('B'),Point('C')), NotCollinear(Point('A'),Point('B'),Point('D')), SameSide(Point('C'),Point('D'),Point('A'),Point('B')), OppositeSide(Point('A'),Point('C'),Point('B'),Point('D')), NotCollinear(Point('B'),Point('C'),Point('D')), OppositeSide(Point('B'),Point('C'),Point('A'),Point('D')), SameSide(Point('B'),Point('D'),Point('A'),Point('C'))]

new_diagrammatic_relations = {SameSide(Point('B'),Point('D'),Point('A'),Point('C')), SameSide(Point('C'),Point('D'),Point('A'),Point('B')), NotCollinear(Point('B'),Point('C'),Point('D')), OppositeSide(Point('B'),Point('C'),Point('A'),Point('D')), OppositeSide(Point('A'),Point('B'),Point('C'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('D')), OppositeSide(Point('A'),Point('C'),Point('B'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('C')), SameSide(Point('A'),Point('D'),Point('B'),Point('C')), NotCollinear(Point('A'),Point('C'),Point('D'))}

