import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('S'),Point('T')) - sympy.simplify('4')), (Length(Point('R'),Point('S')) - sympy.simplify('5')), (Length(Point('R'),Point('T')) - sympy.simplify('3')), Perpendicular(Point('R'),Point('T'),Point('S'),Point('T'))]
goal = sympy.sin(Angle(Point('R'),Point('S'),Point('T')))
solution = '0.6'

diagrammatic_relations = {NotCollinear(Point('R'),Point('S'),Point('T'))}
