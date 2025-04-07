import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


relations = [(Length(Point('B'),Point('D')) - Variable('y')), (Length(Point('B'),Point('C')) - sympy.simplify('30')), (Length(Point('C'),Point('D')) - sympy.simplify('28')), (Length(Point('A'),Point('D')) - sympy.simplify('8')), Between(Point('A'),Point('C'),Point('D')), Collinear(Point('A'),Point('C'),Point('D')), (Angle(Point('A'),Point('B'),Point('C')) - Angle(Point('A'),Point('B'),Point('D')))]
goal = Variable('y')
solution = '12'

diagrammatic_relations = {NotCollinear(Point('A'),Point('B'),Point('C')), SameSide(Point('A'),Point('D'),Point('B'),Point('C')), NotCollinear(Point('A'),Point('B'),Point('D')), OppositeSide(Point('C'),Point('D'),Point('A'),Point('B')), SameSide(Point('A'),Point('C'),Point('B'),Point('D')), NotCollinear(Point('B'),Point('C'),Point('D'))}
