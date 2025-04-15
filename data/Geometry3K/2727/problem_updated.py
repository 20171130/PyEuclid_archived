import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('X'),Point('Z')) - sympy.simplify('9')), (Length(Point('X'),Point('Y')) - sympy.simplify('5')), Perpendicular(Point('X'),Point('Y'),Point('Y'),Point('Z'))]
goal = Angle(Point('X'),Point('Z'),Point('Y'))
solution = '(33.7)/180*pi'

diagrammatic_relations = {NotCollinear(Point('X'),Point('Y'),Point('Z'))}
