import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('A'),Point('Y')) - sympy.simplify('2')), (Length(Point('A'),Point('X')) - (Variable('a') - sympy.simplify('7'))), (Length(Point('A'),Point('W')) - sympy.simplify('10')), (Length(Point('A'),Point('Z')) - ((sympy.simplify('2') * Variable('b')) - sympy.simplify('6'))), Between(Point('A'),Point('X'),Point('Y')), Collinear(Point('A'),Point('X'),Point('Y')), Between(Point('A'),Point('W'),Point('Z')), Collinear(Point('A'),Point('W'),Point('Z')), Parallelogram(Point('W'),Point('X'),Point('Z'),Point('Y'))]
goal = Variable('a')
solution = '9'

diagrammatic_relations = [OppositeSide(Point('W'),Point('Z'),Point('X'),Point('Y')), SameSide(Point('Y'),Point('Z'),Point('W'),Point('X')), SameSide(Point('W'),Point('X'),Point('Y'),Point('Z')), SameSide(Point('W'),Point('Y'),Point('X'),Point('Z')), NotCollinear(Point('A'),Point('Y'),Point('Z')), OppositeSide(Point('W'),Point('Z'),Point('A'),Point('Y')), NotCollinear(Point('X'),Point('Y'),Point('Z')), NotCollinear(Point('A'),Point('W'),Point('Y')), SameSide(Point('A'),Point('Y'),Point('X'),Point('Z')), SameSide(Point('X'),Point('Z'),Point('W'),Point('Y')), SameSide(Point('A'),Point('X'),Point('Y'),Point('Z')), NotCollinear(Point('W'),Point('X'),Point('Y')), OppositeSide(Point('W'),Point('Z'),Point('A'),Point('X')), OppositeSide(Point('X'),Point('Y'),Point('A'),Point('Z')), NotCollinear(Point('A'),Point('X'),Point('Z')), OppositeSide(Point('X'),Point('Y'),Point('W'),Point('Z')), NotCollinear(Point('A'),Point('W'),Point('X')), SameSide(Point('A'),Point('Z'),Point('W'),Point('X')), NotCollinear(Point('W'),Point('Y'),Point('Z')), SameSide(Point('A'),Point('Z'),Point('W'),Point('Y')), SameSide(Point('A'),Point('X'),Point('W'),Point('Y')), NotCollinear(Point('W'),Point('X'),Point('Z')), SameSide(Point('A'),Point('Y'),Point('W'),Point('X')), SameSide(Point('A'),Point('W'),Point('X'),Point('Z')), OppositeSide(Point('X'),Point('Y'),Point('A'),Point('W')), SameSide(Point('A'),Point('W'),Point('Y'),Point('Z'))]
