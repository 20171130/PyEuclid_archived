import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


relations = [(Length(Point('F'),Point('G')) - Variable('x')), (Length(Point('E'),Point('F')) - sympy.simplify('12')), (Length(Point('D'),Point('E')) - sympy.simplify('16')), Between(Point('F'),Point('E'),Point('G')), Collinear(Point('E'),Point('F'),Point('G')), (Length(Point('D'),Point('G')) - Variable('radius_G')), (Length(Point('F'),Point('G')) - Variable('radius_G')), (Angle(Point('E'),Point('D'),Point('G')) - sympy.simplify('pi/2'))]
goal = Variable('x')
solution = '(14)/(3)'

diagrammatic_relations = {NotCollinear(Point('D'),Point('E'),Point('F')), OppositeSide(Point('E'),Point('G'),Point('D'),Point('F')), SameSide(Point('F'),Point('G'),Point('D'),Point('E')), SameSide(Point('E'),Point('F'),Point('D'),Point('G')), NotCollinear(Point('D'),Point('F'),Point('G')), NotCollinear(Point('D'),Point('E'),Point('G'))}
