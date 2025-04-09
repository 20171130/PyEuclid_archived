import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('X'),Point('Y')) - sympy.simplify('6')), (Angle(Point('Y'),Point('X'),Point('Z')) - sympy.simplify('75/180*pi')), (Length(Point('X'),Point('Z')) - Variable('radius_X')), (Length(Point('X'),Point('Y')) - Variable('radius_X'))]
goal = (Angle(Point('Y'),Point('X'),Point('Z')) * Variable('radius_X'))
solution = '7.85'

diagrammatic_relations = [NotCollinear(Point('X'),Point('Y'),Point('Z'))]

new_diagrammatic_relations = {NotCollinear(Point('X'),Point('Y'),Point('Z'))}

