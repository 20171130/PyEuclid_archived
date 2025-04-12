import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [Between(Point('P'),Point('W'),Point('Y')), Collinear(Point('P'),Point('W'),Point('Y')), Between(Point('P'),Point('X'),Point('Z')), Collinear(Point('P'),Point('X'),Point('Z')),\
     (Length(Point('P'),Point('Z')) - ((sympy.simplify('4') * Variable('x')) - sympy.simplify('9'))), (Length(Point('P'),Point('Y')) - ((sympy.simplify('2') * Variable('x')) + sympy.simplify('5'))), Rectangle(Point('W'),Point('X'),Point('Y'),Point('Z'))]
goal = Length(Point('X'),Point('Z'))
solution = '38'

diagrammatic_relations = {NotCollinear(Point('W'),Point('X'),Point('Z')), SameSide(Point('P'),Point('Z'),Point('X'),Point('Y')), OppositeSide(Point('W'),Point('Y'),Point('P'),Point('Z')), NotCollinear(Point('P'),Point('W'),Point('Z')), SameSide(Point('W'),Point('Z'),Point('X'),Point('Y')), NotCollinear(Point('X'),Point('Y'),Point('Z')), SameSide(Point('P'),Point('Y'),Point('W'),Point('X')), NotCollinear(Point('P'),Point('X'),Point('Y')), OppositeSide(Point('W'),Point('Y'),Point('P'),Point('X')), NotCollinear(Point('W'),Point('Y'),Point('Z')), Between(Point('P'),Point('W'),Point('Y')), SameSide(Point('X'),Point('Y'),Point('W'),Point('Z')), NotCollinear(Point('P'),Point('Y'),Point('Z')), OppositeSide(Point('W'),Point('Y'),Point('X'),Point('Z')), NotCollinear(Point('W'),Point('X'),Point('Y')), SameSide(Point('P'),Point('W'),Point('Y'),Point('Z')), OppositeSide(Point('X'),Point('Z'),Point('P'),Point('Y')), OppositeSide(Point('X'),Point('Z'),Point('P'),Point('W')), SameSide(Point('P'),Point('X'),Point('W'),Point('Z')), SameSide(Point('P'),Point('X'),Point('Y'),Point('Z')), SameSide(Point('P'),Point('Z'),Point('W'),Point('X')), SameSide(Point('Y'),Point('Z'),Point('W'),Point('X')), OppositeSide(Point('X'),Point('Z'),Point('W'),Point('Y')), SameSide(Point('W'),Point('X'),Point('Y'),Point('Z')), Between(Point('P'),Point('X'),Point('Z')), NotCollinear(Point('P'),Point('W'),Point('X')), SameSide(Point('P'),Point('W'),Point('X'),Point('Y')), SameSide(Point('P'),Point('Y'),Point('W'),Point('Z'))}
