import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


relations = [Between(Point('D'),Point('A'),Point('B')), Collinear(Point('A'),Point('B'),Point('D')), Between(Point('D'),Point('A'),Point('B')), (Length(Point('A'),Point('C')) - sympy.simplify('8')), (Length(Point('B'),Point('C')) - sympy.simplify('15')), (Length(Point('A'),Point('C')) - sympy.simplify('8')), (Length(Point('B'),Point('C')) - sympy.simplify('15')), ((Length(Point('A'),Point('B')) - Variable('radius_D')) - Variable('radius_D')), Collinear(Point('A'),Point('B'),Point('D')), (Length(Point('B'),Point('D')) - Variable('radius_D')), (Length(Point('A'),Point('D')) - Variable('radius_D')), (Length(Point('C'),Point('D')) - Variable('radius_D'))]
goal = Length(Point('A'),Point('D'))
solution = '8.5'

diagrammatic_relations = {OppositeSide(Point('A'),Point('B'),Point('C'),Point('D')), NotCollinear(Point('A'),Point('C'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('C')), SameSide(Point('A'),Point('D'),Point('B'),Point('C')), NotCollinear(Point('B'),Point('C'),Point('D')), SameSide(Point('B'),Point('D'),Point('A'),Point('C'))}
