import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('S'),Point('T')) - 6), (Length(Point('W'),Point('X')) - 5), Similar(Point('W'),Point('Z'),Point('X'),Point('S'),Point('R'),Point('T')), (Length(Point('S'),Point('T')) - sympy.simplify('6')), (Length(Point('W'),Point('X')) - 5), (((Length(Point('R'),Point('S')) + Length(Point('R'),Point('T'))) + Length(Point('S'),Point('T'))) - 15), Similar(Point('W'),Point('Z'),Point('X'),Point('S'),Point('R'),Point('T')), (Length(Point('S'),Point('T')) - 6), (Length(Point('W'),Point('X')) - 5), (((Length(Point('R'),Point('S')) + Length(Point('R'),Point('T'))) + Length(Point('S'),Point('T'))) - 15)]
goal = ((Length(Point('W'),Point('Z')) + Length(Point('X'),Point('Z'))) + Length(Point('W'),Point('X')))
solution = '12.5'

diagrammatic_relations = {NotCollinear(Point('R'),Point('S'),Point('T'))}
