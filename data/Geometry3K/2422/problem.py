import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('A'),Point('D')) - sympy.simplify('14')), (Angle(Point('A'),Point('O'),Point('B')) - sympy.simplify('80/180*pi')), Between(Point('O'),Point('A'),Point('D')), Collinear(Point('A'),Point('D'),Point('O')), (Length(Point('A'),Point('O')) - Variable('radius_O')), (Length(Point('B'),Point('O')) - Variable('radius_O')), (Length(Point('D'),Point('O')) - Variable('radius_O'))]
goal = (Angle(Point('A'),Point('O'),Point('B')) * Variable('radius_O'))
solution = '9.77'

diagrammatic_relations = [NotCollinear(Point('B'),Point('D'),Point('O')), SameSide(Point('D'),Point('O'),Point('A'),Point('B')), NotCollinear(Point('A'),Point('B'),Point('D')), SameSide(Point('A'),Point('O'),Point('B'),Point('D')), OppositeSide(Point('A'),Point('D'),Point('B'),Point('O')), NotCollinear(Point('A'),Point('B'),Point('O'))]

new_diagrammatic_relations = {NotCollinear(Point('A'),Point('B'),Point('O')), SameSide(Point('A'),Point('O'),Point('B'),Point('D')), SameSide(Point('D'),Point('O'),Point('A'),Point('B')), NotCollinear(Point('A'),Point('B'),Point('D')), OppositeSide(Point('A'),Point('D'),Point('B'),Point('O')), Between(Point('O'),Point('A'),Point('D')), NotCollinear(Point('B'),Point('D'),Point('O'))}

