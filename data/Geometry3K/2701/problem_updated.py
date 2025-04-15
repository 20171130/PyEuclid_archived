import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('Y'),Point('Z')) - sympy.simplify('28')), (Length(Point('X'),Point('Y')) - sympy.simplify('24')), (Angle(Point('X'),Point('W'),Point('Z')) - sympy.simplify('105/180*pi')), Parallelogram(Point('W'),Point('X'),Point('Y'),Point('Z')), Parallelogram(Point('W'),Point('X'),Point('Y'),Point('Z'))]
goal = Angle(Point('X'),Point('Y'),Point('Z'))
solution = '(105)/180*pi'

diagrammatic_relations = {OppositeSide(Point('W'),Point('Y'),Point('X'),Point('Z')), NotCollinear(Point('W'),Point('X'),Point('Z')), NotCollinear(Point('W'),Point('X'),Point('Y')), SameSide(Point('Y'),Point('Z'),Point('W'),Point('X')), NotCollinear(Point('W'),Point('Y'),Point('Z')), OppositeSide(Point('X'),Point('Z'),Point('W'),Point('Y')), SameSide(Point('W'),Point('Z'),Point('X'),Point('Y')), SameSide(Point('W'),Point('X'),Point('Y'),Point('Z')), NotCollinear(Point('X'),Point('Y'),Point('Z')), SameSide(Point('X'),Point('Y'),Point('W'),Point('Z'))}
