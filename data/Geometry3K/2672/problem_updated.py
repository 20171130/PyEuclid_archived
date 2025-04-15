import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('B'),Point('D')) - Variable('y')), (Length(Point('B'),Point('C')) - sympy.simplify('30')), (Length(Point('C'),Point('D')) - sympy.simplify('28')), (Length(Point('A'),Point('D')) - sympy.simplify('8')), Between(Point('A'),Point('C'),Point('D')), Collinear(Point('A'),Point('C'),Point('D')), (Angle(Point('A'),Point('B'),Point('C')) - Angle(Point('A'),Point('B'),Point('D')))]
goal = Variable('y')
solution = '12'

diagrammatic_relations = {NotCollinear(Point('B'),Point('C'),Point('D')), OppositeSide(Point('C'),Point('D'),Point('A'),Point('B')), NotCollinear(Point('A'),Point('B'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('C')), SameSide(Point('A'),Point('C'),Point('B'),Point('D')), SameSide(Point('A'),Point('D'),Point('B'),Point('C')), Between(Point('A'),Point('C'),Point('D'))}
