import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


relations = [(Angle(Point('D'),Point('C'),Point('E')) - ((((sympy.simplify('5') * Variable('x')) - sympy.simplify('12')) / sympy.simplify('180')) * sympy.simplify('pi'))), (Angle(Point('C'),Point('E'),Point('D')) - (((sympy.simplify('3') * Variable('x')) / sympy.simplify('180')) * sympy.simplify('pi'))), Between(Point('B'),Point('C'),Point('E')), Collinear(Point('B'),Point('C'),Point('E')), (Length(Point('B'),Point('E')) - Variable('radius_B')), (Length(Point('B'),Point('C')) - Variable('radius_B')), (Length(Point('B'),Point('D')) - Variable('radius_B'))]
goal = Variable('x')
solution = '12.75'

diagrammatic_relations = {OppositeSide(Point('C'),Point('E'),Point('B'),Point('D')), NotCollinear(Point('C'),Point('D'),Point('E')), NotCollinear(Point('B'),Point('D'),Point('E')), NotCollinear(Point('B'),Point('C'),Point('D')), SameSide(Point('B'),Point('E'),Point('C'),Point('D')), SameSide(Point('B'),Point('C'),Point('D'),Point('E'))}
