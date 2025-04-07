import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


relations = [Between(Point('M'),Point('X'),Point('Y')), Collinear(Point('M'),Point('X'),Point('Y')), Between(Point('N'),Point('X'),Point('Z')), Collinear(Point('N'),Point('X'),Point('Z')), Parallel(Point('M'),Point('N'),Point('Y'),Point('Z')), (Length(Point('M'),Point('X')) - sympy.simplify('4')), (Length(Point('N'),Point('X')) - sympy.simplify('6')), (Length(Point('N'),Point('Z')) - sympy.simplify('9')), (Length(Point('M'),Point('X')) - sympy.simplify('4')), (Length(Point('N'),Point('X')) - sympy.simplify('6')), (Length(Point('N'),Point('Z')) - sympy.simplify('9'))]
goal = Length(Point('X'),Point('Y'))
solution = '10'

diagrammatic_relations = {NotCollinear(Point('M'),Point('N'),Point('Z')), NotCollinear(Point('M'),Point('Y'),Point('Z')), OppositeSide(Point('X'),Point('Z'),Point('M'),Point('N')), OppositeSide(Point('X'),Point('Y'),Point('M'),Point('N')), SameSide(Point('N'),Point('Z'),Point('M'),Point('Y')), SameSide(Point('M'),Point('X'),Point('N'),Point('Y')), SameSide(Point('M'),Point('Y'),Point('X'),Point('Z')), SameSide(Point('M'),Point('N'),Point('Y'),Point('Z')), OppositeSide(Point('N'),Point('Y'),Point('M'),Point('Z')), SameSide(Point('N'),Point('Z'),Point('X'),Point('Y')), OppositeSide(Point('M'),Point('Z'),Point('N'),Point('Y')), SameSide(Point('N'),Point('Z'),Point('M'),Point('X')), SameSide(Point('Y'),Point('Z'),Point('M'),Point('N')), OppositeSide(Point('X'),Point('Z'),Point('N'),Point('Y')), SameSide(Point('N'),Point('X'),Point('Y'),Point('Z')), SameSide(Point('M'),Point('Y'),Point('N'),Point('Z')), NotCollinear(Point('X'),Point('Y'),Point('Z')), SameSide(Point('M'),Point('X'),Point('Y'),Point('Z')), SameSide(Point('N'),Point('X'),Point('M'),Point('Z')), NotCollinear(Point('N'),Point('Y'),Point('Z')), NotCollinear(Point('N'),Point('X'),Point('Y')), NotCollinear(Point('M'),Point('N'),Point('Y')), NotCollinear(Point('M'),Point('X'),Point('Z')), OppositeSide(Point('X'),Point('Y'),Point('M'),Point('Z')), NotCollinear(Point('M'),Point('N'),Point('X')), SameSide(Point('M'),Point('Y'),Point('N'),Point('X'))}
