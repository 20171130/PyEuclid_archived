import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('V'),Point('X')) - sympy.simplify('75')), (Length(Point('V'),Point('W')) - sympy.simplify('72')), (Length(Point('W'),Point('X')) - sympy.simplify('21')), Perpendicular(Point('V'),Point('W'),Point('W'),Point('X'))]
goal = sympy.cos(Angle(Point('V'),Point('X'),Point('W')))
solution = '0.28'

diagrammatic_relations = [NotCollinear(Point('V'),Point('W'),Point('X'))]
