import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


relations = [(Length(Point('B'),Point('W')) - sympy.simplify('8')), (Length(Point('B'),Point('X')) - (Variable('s') - sympy.simplify('7'))), (Length(Point('B'),Point('Y')) - sympy.simplify('6')), (Length(Point('B'),Point('Z')) - ((sympy.simplify('2') * Variable('t')) - sympy.simplify('6'))), Between(Point('B'),Point('W'),Point('Z')), Collinear(Point('B'),Point('W'),Point('Z')), Between(Point('B'),Point('X'),Point('Y')), Collinear(Point('B'),Point('X'),Point('Y')), Parallelogram(Point('W'),Point('X'),Point('Z'),Point('Y'))]
goal = Variable('t')
solution = '7'

diagrammatic_relations = {SameSide(Point('B'),Point('X'),Point('W'),Point('Y')), OppositeSide(Point('W'),Point('Z'),Point('X'),Point('Y')), SameSide(Point('B'),Point('Z'),Point('W'),Point('X')), SameSide(Point('Y'),Point('Z'),Point('W'),Point('X')), NotCollinear(Point('B'),Point('W'),Point('Y')), OppositeSide(Point('X'),Point('Y'),Point('B'),Point('W')), SameSide(Point('B'),Point('Y'),Point('W'),Point('X')), SameSide(Point('W'),Point('X'),Point('Y'),Point('Z')), SameSide(Point('W'),Point('Y'),Point('X'),Point('Z')), SameSide(Point('B'),Point('W'),Point('Y'),Point('Z')), NotCollinear(Point('X'),Point('Y'),Point('Z')), SameSide(Point('X'),Point('Z'),Point('W'),Point('Y')), NotCollinear(Point('W'),Point('X'),Point('Y')), OppositeSide(Point('X'),Point('Y'),Point('B'),Point('Z')), OppositeSide(Point('X'),Point('Y'),Point('W'),Point('Z')), NotCollinear(Point('B'),Point('W'),Point('X')), NotCollinear(Point('W'),Point('Y'),Point('Z')), OppositeSide(Point('W'),Point('Z'),Point('B'),Point('Y')), NotCollinear(Point('B'),Point('X'),Point('Z')), SameSide(Point('B'),Point('X'),Point('Y'),Point('Z')), SameSide(Point('B'),Point('Y'),Point('X'),Point('Z')), NotCollinear(Point('B'),Point('Y'),Point('Z')), SameSide(Point('B'),Point('Z'),Point('W'),Point('Y')), NotCollinear(Point('W'),Point('X'),Point('Z')), OppositeSide(Point('W'),Point('Z'),Point('B'),Point('X')), SameSide(Point('B'),Point('W'),Point('X'),Point('Z'))}
