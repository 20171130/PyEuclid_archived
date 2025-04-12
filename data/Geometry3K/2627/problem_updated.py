import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Angle(Point('R'),Point('T'),Point('S')) - (((sympy.simplify('2') * Variable('x')) / sympy.simplify('180')) * sympy.simplify('pi'))), (Angle(Point('S'),Point('R'),Point('T')) - ((Variable('x') / sympy.simplify('180')) * sympy.simplify('pi'))), Between(Point('B'),Point('R'),Point('T')), Collinear(Point('B'),Point('R'),Point('T')), (Length(Point('B'),Point('R')) - Variable('radius_B')), (Length(Point('B'),Point('T')) - Variable('radius_B')), (Length(Point('B'),Point('S')) - Variable('radius_B'))]
goal = Variable('x')
solution = '30'

diagrammatic_relations = {NotCollinear(Point('R'),Point('S'),Point('T')), OppositeSide(Point('R'),Point('T'),Point('B'),Point('S')), NotCollinear(Point('B'),Point('S'),Point('T')), NotCollinear(Point('B'),Point('R'),Point('S')), SameSide(Point('B'),Point('T'),Point('R'),Point('S')), Between(Point('B'),Point('R'),Point('T')), SameSide(Point('B'),Point('R'),Point('S'),Point('T'))}
