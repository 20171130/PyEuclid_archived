import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Angle(Point('Y'),Point('X'),Point('Z')) - sympy.simplify('105/180*pi')), (Angle(Point('X'),Point('Y'),Point('Z')) - Variable('angle_1')), (Angle(Point('X'),Point('W'),Point('Z')) - sympy.simplify('23/180*pi')), (Angle(Point('W'),Point('Z'),Point('X')) - sympy.simplify('24/180*pi')), (Angle(Point('X'),Point('Z'),Point('Y')) - Variable('angle_2')), (Angle(Point('W'),Point('X'),Point('Z')) - Variable('angle_3')), (Angle(Point('X'),Point('Y'),Point('Z')) - Angle(Point('X'),Point('Z'),Point('Y')))]
goal = Variable('angle_1')
solution = '(37.5)/180*pi'

diagrammatic_relations = {OppositeSide(Point('W'),Point('Y'),Point('X'),Point('Z')), NotCollinear(Point('W'),Point('X'),Point('Z')), NotCollinear(Point('W'),Point('X'),Point('Y')), OppositeSide(Point('Y'),Point('Z'),Point('W'),Point('X')), NotCollinear(Point('W'),Point('Y'),Point('Z')), SameSide(Point('X'),Point('Z'),Point('W'),Point('Y')), SameSide(Point('W'),Point('X'),Point('Y'),Point('Z')), NotCollinear(Point('X'),Point('Y'),Point('Z')), SameSide(Point('X'),Point('Y'),Point('W'),Point('Z')), OppositeSide(Point('W'),Point('Z'),Point('X'),Point('Y'))}
