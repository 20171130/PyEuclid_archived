import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('A'),Point('D')) - sympy.simplify('9')), (Length(Point('C'),Point('D')) - Variable('x')), (Length(Point('C'),Point('E')) - sympy.simplify('6')), Between(Point('E'),Point('A'),Point('C')), Collinear(Point('A'),Point('C'),Point('E')), (Length(Point('A'),Point('D')) - Variable('radius_A')), (Length(Point('A'),Point('E')) - Variable('radius_A')), (Angle(Point('A'),Point('D'),Point('C')) - sympy.simplify('pi/2'))]
goal = Variable('x')
solution = '12'

diagrammatic_relations = [NotCollinear(Point('A'),Point('C'),Point('D')), SameSide(Point('C'),Point('E'),Point('A'),Point('D')), SameSide(Point('A'),Point('E'),Point('C'),Point('D')), NotCollinear(Point('A'),Point('D'),Point('E')), OppositeSide(Point('A'),Point('C'),Point('D'),Point('E')), NotCollinear(Point('C'),Point('D'),Point('E'))]

new_diagrammatic_relations = {NotCollinear(Point('C'),Point('D'),Point('E')), NotCollinear(Point('A'),Point('D'),Point('E')), Between(Point('E'),Point('A'),Point('C')), SameSide(Point('A'),Point('E'),Point('C'),Point('D')), SameSide(Point('C'),Point('E'),Point('A'),Point('D')), OppositeSide(Point('A'),Point('C'),Point('D'),Point('E')), NotCollinear(Point('A'),Point('C'),Point('D'))}

