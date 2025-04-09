import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('X'),Point('Y')) - (sympy.simplify('18') + (sympy.simplify('2') * Variable('y')))), (Length(Point('X'),Point('Z')) - ((sympy.simplify('5') * Variable('y')) - sympy.simplify('6'))), Between(Point('W'),Point('Y'),Point('Z')), Collinear(Point('W'),Point('Y'),Point('Z')), (Length(Point('W'),Point('Y')) - Length(Point('W'),Point('Z'))), Perpendicular(Point('W'),Point('X'),Point('W'),Point('Z'))]
goal = Length(Point('X'),Point('Z'))
solution = '34'

diagrammatic_relations = [NotCollinear(Point('W'),Point('X'),Point('Y')), SameSide(Point('W'),Point('Y'),Point('X'),Point('Z')), SameSide(Point('W'),Point('Z'),Point('X'),Point('Y')), NotCollinear(Point('W'),Point('X'),Point('Z')), NotCollinear(Point('X'),Point('Y'),Point('Z')), OppositeSide(Point('Y'),Point('Z'),Point('W'),Point('X'))]

new_diagrammatic_relations = {NotCollinear(Point('W'),Point('X'),Point('Z')), OppositeSide(Point('Y'),Point('Z'),Point('W'),Point('X')), NotCollinear(Point('W'),Point('X'),Point('Y')), Between(Point('W'),Point('Y'),Point('Z')), SameSide(Point('W'),Point('Y'),Point('X'),Point('Z')), SameSide(Point('W'),Point('Z'),Point('X'),Point('Y')), NotCollinear(Point('X'),Point('Y'),Point('Z'))}

