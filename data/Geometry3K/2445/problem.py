import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Angle(Point('A'),Point('E'),Point('D')) - sympy.simplify('45/180*pi')), (Length(Point('A'),Point('G')) - Variable('x')), (Length(Point('A'),Point('E')) - sympy.simplify('8')), (Length(Point('D'),Point('G')) - Variable('y')), (Angle(Point('A'),Point('D'),Point('E')) - sympy.simplify('30/180*pi')), Between(Point('G'),Point('D'),Point('E')), Collinear(Point('D'),Point('E'),Point('G')), Perpendicular(Point('A'),Point('G'),Point('D'),Point('G'))]
goal = Variable('x')
solution = '4*sqrt(2)'

diagrammatic_relations = [NotCollinear(Point('A'),Point('E'),Point('G')), OppositeSide(Point('D'),Point('E'),Point('A'),Point('G')), NotCollinear(Point('A'),Point('D'),Point('E')), SameSide(Point('D'),Point('G'),Point('A'),Point('E')), NotCollinear(Point('A'),Point('D'),Point('G')), SameSide(Point('E'),Point('G'),Point('A'),Point('D'))]

new_diagrammatic_relations = {Between(Point('G'),Point('D'),Point('E')), NotCollinear(Point('A'),Point('D'),Point('E')), OppositeSide(Point('D'),Point('E'),Point('A'),Point('G')), SameSide(Point('D'),Point('G'),Point('A'),Point('E')), NotCollinear(Point('A'),Point('E'),Point('G')), SameSide(Point('E'),Point('G'),Point('A'),Point('D')), NotCollinear(Point('A'),Point('D'),Point('G'))}

