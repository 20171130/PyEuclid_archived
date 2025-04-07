import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


relations = [(Length(Point('W'),Point('X')) - ((sympy.simplify('2') * Variable('x')) + sympy.simplify('9'))), (Length(Point('X'),Point('Y')) - ((sympy.simplify('3') * Variable('x')) + sympy.simplify('6'))), (Length(Point('Y'),Point('Z')) - Variable('radius_Z')), (Length(Point('W'),Point('Z')) - Variable('radius_Z')), (Angle(Point('X'),Point('W'),Point('Z')) - sympy.simplify('pi/2')), (Angle(Point('X'),Point('Y'),Point('Z')) - sympy.simplify('pi/2'))]
goal = Variable('x')
solution = '3'

diagrammatic_relations = {NotCollinear(Point('W'),Point('X'),Point('Y')), SameSide(Point('Y'),Point('Z'),Point('W'),Point('X')), SameSide(Point('W'),Point('Z'),Point('X'),Point('Y')), OppositeSide(Point('X'),Point('Z'),Point('W'),Point('Y')), OppositeSide(Point('W'),Point('Y'),Point('X'),Point('Z')), NotCollinear(Point('W'),Point('X'),Point('Z')), NotCollinear(Point('X'),Point('Y'),Point('Z')), SameSide(Point('W'),Point('X'),Point('Y'),Point('Z')), NotCollinear(Point('W'),Point('Y'),Point('Z')), SameSide(Point('X'),Point('Y'),Point('W'),Point('Z'))}
