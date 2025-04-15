import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('M'),Point('Q')) - sympy.simplify('5')), (Length(Point('N'),Point('O')) - (sympy.simplify('3') + (sympy.simplify('3') / sympy.simplify('5')))), (Length(Point('M'),Point('N')) - sympy.simplify('6')), (Length(Point('P'),Point('Q')) - Variable('x')), Between(Point('N'),Point('M'),Point('O')), Collinear(Point('M'),Point('N'),Point('O')), Between(Point('Q'),Point('M'),Point('P')), Collinear(Point('M'),Point('P'),Point('Q')), Parallel(Point('N'),Point('Q'),Point('O'),Point('P'))]
goal = Length(Point('P'),Point('Q'))
solution = '3'

diagrammatic_relations = {NotCollinear(Point('M'),Point('N'),Point('Q')), NotCollinear(Point('M'),Point('O'),Point('Q')), Between(Point('Q'),Point('M'),Point('P')), Between(Point('N'),Point('M'),Point('O')), NotCollinear(Point('M'),Point('N'),Point('P')), SameSide(Point('M'),Point('N'),Point('O'),Point('Q')), SameSide(Point('N'),Point('Q'),Point('O'),Point('P')), NotCollinear(Point('O'),Point('P'),Point('Q')), SameSide(Point('N'),Point('O'),Point('P'),Point('Q')), SameSide(Point('N'),Point('O'),Point('M'),Point('P')), NotCollinear(Point('N'),Point('O'),Point('Q')), SameSide(Point('P'),Point('Q'),Point('M'),Point('N')), OppositeSide(Point('M'),Point('P'),Point('O'),Point('Q')), NotCollinear(Point('N'),Point('P'),Point('Q')), OppositeSide(Point('O'),Point('Q'),Point('N'),Point('P')), OppositeSide(Point('M'),Point('O'),Point('N'),Point('P')), SameSide(Point('O'),Point('P'),Point('N'),Point('Q')), NotCollinear(Point('M'),Point('O'),Point('P')), OppositeSide(Point('N'),Point('P'),Point('O'),Point('Q')), NotCollinear(Point('N'),Point('O'),Point('P')), SameSide(Point('M'),Point('Q'),Point('N'),Point('P')), SameSide(Point('P'),Point('Q'),Point('M'),Point('O')), OppositeSide(Point('M'),Point('P'),Point('N'),Point('Q')), SameSide(Point('N'),Point('O'),Point('M'),Point('Q')), SameSide(Point('M'),Point('Q'),Point('O'),Point('P')), SameSide(Point('M'),Point('N'),Point('O'),Point('P')), SameSide(Point('P'),Point('Q'),Point('N'),Point('O')), OppositeSide(Point('M'),Point('O'),Point('N'),Point('Q'))}
