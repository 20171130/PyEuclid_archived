import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('X'),Point('Y')) - ((sympy.simplify('3') * Variable('a')) + sympy.simplify('7'))), (Length(Point('W'),Point('X')) - (Variable('b') + sympy.simplify('11'))), (Length(Point('W'),Point('Z')) - (sympy.simplify('4') * Variable('a'))), (Length(Point('Y'),Point('Z')) - (sympy.simplify('2') * Variable('b'))), Parallelogram(Point('W'),Point('X'),Point('Y'),Point('Z'))]
goal = Variable('b')
solution = '11'

diagrammatic_relations = [NotCollinear(Point('W'),Point('X'),Point('Y')), SameSide(Point('Y'),Point('Z'),Point('W'),Point('X')), SameSide(Point('W'),Point('Z'),Point('X'),Point('Y')), OppositeSide(Point('X'),Point('Z'),Point('W'),Point('Y')), OppositeSide(Point('W'),Point('Y'),Point('X'),Point('Z')), NotCollinear(Point('W'),Point('X'),Point('Z')), NotCollinear(Point('X'),Point('Y'),Point('Z')), SameSide(Point('W'),Point('X'),Point('Y'),Point('Z')), NotCollinear(Point('W'),Point('Y'),Point('Z')), SameSide(Point('X'),Point('Y'),Point('W'),Point('Z'))]

new_diagrammatic_relations = {OppositeSide(Point('W'),Point('Y'),Point('X'),Point('Z')), NotCollinear(Point('W'),Point('X'),Point('Z')), NotCollinear(Point('W'),Point('X'),Point('Y')), SameSide(Point('Y'),Point('Z'),Point('W'),Point('X')), NotCollinear(Point('W'),Point('Y'),Point('Z')), OppositeSide(Point('X'),Point('Z'),Point('W'),Point('Y')), SameSide(Point('W'),Point('Z'),Point('X'),Point('Y')), SameSide(Point('W'),Point('X'),Point('Y'),Point('Z')), NotCollinear(Point('X'),Point('Y'),Point('Z')), SameSide(Point('X'),Point('Y'),Point('W'),Point('Z'))}

