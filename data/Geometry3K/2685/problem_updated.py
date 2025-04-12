import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('S'),Point('T')) - ((sympy.simplify('2') * Variable('y')) + sympy.simplify('12'))), (Length(Point('R'),Point('T')) - Variable('x')), (Length(Point('Q'),Point('T')) - (sympy.simplify('5') * Variable('y'))), (Length(Point('P'),Point('T')) - ((sympy.simplify('5') * Variable('x')) - sympy.simplify('28'))), Between(Point('T'),Point('Q'),Point('S')), Collinear(Point('Q'),Point('S'),Point('T')), Between(Point('T'),Point('P'),Point('R')), Collinear(Point('P'),Point('R'),Point('T')), Parallelogram(Point('P'),Point('Q'),Point('R'),Point('S'))]
goal = Variable('y')
solution = '4'

diagrammatic_relations = {NotCollinear(Point('R'),Point('S'),Point('T')), NotCollinear(Point('Q'),Point('R'),Point('T')), SameSide(Point('Q'),Point('T'),Point('R'),Point('S')), OppositeSide(Point('Q'),Point('S'),Point('P'),Point('R')), OppositeSide(Point('P'),Point('R'),Point('Q'),Point('S')), SameSide(Point('P'),Point('S'),Point('Q'),Point('R')), OppositeSide(Point('Q'),Point('S'),Point('R'),Point('T')), OppositeSide(Point('P'),Point('R'),Point('Q'),Point('T')), NotCollinear(Point('P'),Point('Q'),Point('T')), SameSide(Point('P'),Point('T'),Point('R'),Point('S')), NotCollinear(Point('Q'),Point('R'),Point('S')), SameSide(Point('P'),Point('T'),Point('Q'),Point('R')), SameSide(Point('R'),Point('T'),Point('P'),Point('S')), Between(Point('T'),Point('P'),Point('R')), NotCollinear(Point('P'),Point('R'),Point('S')), NotCollinear(Point('P'),Point('S'),Point('T')), OppositeSide(Point('Q'),Point('S'),Point('P'),Point('T')), NotCollinear(Point('P'),Point('Q'),Point('R')), Between(Point('T'),Point('Q'),Point('S')), NotCollinear(Point('P'),Point('Q'),Point('S')), SameSide(Point('R'),Point('T'),Point('P'),Point('Q')), SameSide(Point('Q'),Point('T'),Point('P'),Point('S')), SameSide(Point('R'),Point('S'),Point('P'),Point('Q')), SameSide(Point('S'),Point('T'),Point('P'),Point('Q')), SameSide(Point('S'),Point('T'),Point('Q'),Point('R')), OppositeSide(Point('P'),Point('R'),Point('S'),Point('T')), SameSide(Point('Q'),Point('R'),Point('P'),Point('S')), SameSide(Point('P'),Point('Q'),Point('R'),Point('S'))}
