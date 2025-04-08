import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('T'),Point('Y')) - (sympy.simplify('4') * Variable('x'))), (Length(Point('Y'),Point('W')) - ((sympy.simplify('2') * Variable('x')) + sympy.simplify('10'))), Congruent(Point('T'),Point('X'),Point('Y'),Point('W'),Point('X'),Point('Y')), (Length(Point('A'),Point('T')) - Variable('radius_A')), (Length(Point('A'),Point('Y')) - Variable('radius_A')), (Length(Point('A'),Point('W')) - Variable('radius_A'))]
goal = Variable('x')
solution = '5'

diagrammatic_relations = [NotCollinear(Point('W'),Point('X'),Point('Y')), SameSide(Point('X'),Point('Y'),Point('T'),Point('W')), SameSide(Point('T'),Point('X'),Point('W'),Point('Y')), SameSide(Point('W'),Point('X'),Point('T'),Point('Y')), NotCollinear(Point('T'),Point('W'),Point('X')), NotCollinear(Point('T'),Point('X'),Point('Y')), OppositeSide(Point('T'),Point('W'),Point('X'),Point('Y')), NotCollinear(Point('T'),Point('W'),Point('Y')), OppositeSide(Point('W'),Point('Y'),Point('T'),Point('X')), OppositeSide(Point('T'),Point('Y'),Point('W'),Point('X'))]
