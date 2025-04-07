import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


relations = [Between(Point('P'),Point('W'),Point('Y')), Collinear(Point('P'),Point('W'),Point('Y')), Between(Point('P'),Point('X'),Point('Z')), Collinear(Point('P'),Point('X'),Point('Z')),\
     (Length(Point('P'),Point('Z')) - ((sympy.simplify('4') * Variable('x')) - sympy.simplify('9'))), (Length(Point('P'),Point('Y')) - ((sympy.simplify('2') * Variable('x')) + sympy.simplify('5'))), Rectangle(Point('W'),Point('X'),Point('Y'),Point('Z'))]
goal = Length(Point('X'),Point('Z'))
solution = '38'

diagrammatic_relations = {SameSide(Point('P'),Point('W'),Point('X'),Point('Y')), SameSide(Point('Y'),Point('Z'),Point('W'),Point('X')), SameSide(Point('W'),Point('Z'),Point('X'),Point('Y')), OppositeSide(Point('X'),Point('Z'),Point('W'),Point('Y')), NotCollinear(Point('P'),Point('X'),Point('Y')), SameSide(Point('P'),Point('X'),Point('W'),Point('Z')), SameSide(Point('W'),Point('X'),Point('Y'),Point('Z')), OppositeSide(Point('W'),Point('Y'),Point('P'),Point('X')), SameSide(Point('P'),Point('W'),Point('Y'),Point('Z')), SameSide(Point('P'),Point('X'),Point('Y'),Point('Z')), SameSide(Point('P'),Point('Z'),Point('W'),Point('X')), NotCollinear(Point('X'),Point('Y'),Point('Z')), OppositeSide(Point('X'),Point('Z'),Point('P'),Point('Y')), SameSide(Point('X'),Point('Y'),Point('W'),Point('Z')), NotCollinear(Point('W'),Point('X'),Point('Y')), OppositeSide(Point('X'),Point('Z'),Point('P'),Point('W')), SameSide(Point('P'),Point('Y'),Point('W'),Point('Z')), NotCollinear(Point('P'),Point('W'),Point('X')), NotCollinear(Point('W'),Point('Y'),Point('Z')), NotCollinear(Point('P'),Point('W'),Point('Z')), SameSide(Point('P'),Point('Z'),Point('X'),Point('Y')), NotCollinear(Point('P'),Point('Y'),Point('Z')), OppositeSide(Point('W'),Point('Y'),Point('X'),Point('Z')), OppositeSide(Point('W'),Point('Y'),Point('P'),Point('Z')), NotCollinear(Point('W'),Point('X'),Point('Z')), SameSide(Point('P'),Point('Y'),Point('W'),Point('X')), Between(Point('P'),Point('X'),Point('Z'))}
