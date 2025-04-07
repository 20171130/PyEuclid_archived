import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


relations = [(Length(Point('W'),Point('X')) - sympy.simplify('6')), (Length(Point('P'),Point('X')) - sympy.simplify('4')), Between(Point('P'),Point('X'),Point('Z')), Collinear(Point('P'),Point('X'),Point('Z')), Between(Point('P'),Point('W'),Point('Y')), Collinear(Point('P'),Point('W'),Point('Y')), (Length(Point('W'),Point('Z')) - Length(Point('Y'),Point('Z'))), (Length(Point('W'),Point('X')) - Length(Point('X'),Point('Y'))), Quadrilateral(Point('W'),Point('X'),Point('Y'),Point('Z'))]
goal = Length(Point('P'),Point('W'))
solution = 'sqrt(20)'

diagrammatic_relations = {SameSide(Point('P'),Point('W'),Point('X'),Point('Y')), SameSide(Point('Y'),Point('Z'),Point('W'),Point('X')), SameSide(Point('W'),Point('Z'),Point('X'),Point('Y')), OppositeSide(Point('X'),Point('Z'),Point('W'),Point('Y')), NotCollinear(Point('P'),Point('X'),Point('Y')), SameSide(Point('P'),Point('X'),Point('W'),Point('Z')), SameSide(Point('W'),Point('X'),Point('Y'),Point('Z')), OppositeSide(Point('W'),Point('Y'),Point('P'),Point('X')), SameSide(Point('P'),Point('W'),Point('Y'),Point('Z')), SameSide(Point('P'),Point('X'),Point('Y'),Point('Z')), SameSide(Point('P'),Point('Z'),Point('W'),Point('X')), NotCollinear(Point('X'),Point('Y'),Point('Z')), OppositeSide(Point('X'),Point('Z'),Point('P'),Point('Y')), SameSide(Point('X'),Point('Y'),Point('W'),Point('Z')), NotCollinear(Point('W'),Point('X'),Point('Y')), OppositeSide(Point('X'),Point('Z'),Point('P'),Point('W')), SameSide(Point('P'),Point('Y'),Point('W'),Point('Z')), NotCollinear(Point('P'),Point('W'),Point('X')), NotCollinear(Point('W'),Point('Y'),Point('Z')), NotCollinear(Point('P'),Point('W'),Point('Z')), SameSide(Point('P'),Point('Z'),Point('X'),Point('Y')), NotCollinear(Point('P'),Point('Y'),Point('Z')), OppositeSide(Point('W'),Point('Y'),Point('X'),Point('Z')), OppositeSide(Point('W'),Point('Y'),Point('P'),Point('Z')), NotCollinear(Point('W'),Point('X'),Point('Z')), SameSide(Point('P'),Point('Y'),Point('W'),Point('X'))}
