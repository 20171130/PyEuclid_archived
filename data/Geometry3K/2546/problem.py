import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('W'),Point('X')) - sympy.simplify('2')), (Angle(Point('W'),Point('X'),Point('Y')) - sympy.simplify('52/180*pi')), (Length(Point('X'),Point('Y')) - Variable('radius_X')), (Length(Point('W'),Point('X')) - Variable('radius_X'))]
goal = (Angle(Point('W'),Point('X'),Point('Y')) * Variable('radius_X'))
solution = '1.8'

diagrammatic_relations = [NotCollinear(Point('W'),Point('X'),Point('Y'))]

new_diagrammatic_relations = {NotCollinear(Point('W'),Point('X'),Point('Y'))}

