import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


relations = [(Perpendicular(Point('M'),Point('P'),Point('P'),Point('A'))), (Length(Point('B'),Point('P')) - sympy.simplify('5')), (Length(Point('M'),Point('P')) - sympy.simplify('16')), (Length(Point('A'),Point('P')) - Variable('x')), Between(Point('C'),Point('A'),Point('M')), Collinear(Point('A'),Point('C'),Point('M')), Between(Point('P'),Point('B'),Point('M')), Collinear(Point('B'),Point('M'),Point('P')), (Length(Point('M'),Point('A')) - sympy.simplify('20')), (Length(Point('A'),Point('P')) - Variable('radius_A')), (Length(Point('A'),Point('C')) - Variable('radius_A'))]
goal = Variable('x')
solution = '12'

diagrammatic_relations = {SameSide(Point('B'),Point('P'),Point('C'),Point('M')), NotCollinear(Point('C'),Point('M'),Point('P')), NotCollinear(Point('A'),Point('B'),Point('M')), SameSide(Point('A'),Point('B'),Point('C'),Point('P')), NotCollinear(Point('A'),Point('B'),Point('P')), NotCollinear(Point('A'),Point('M'),Point('P')), OppositeSide(Point('B'),Point('M'),Point('A'),Point('P')), SameSide(Point('C'),Point('M'),Point('A'),Point('B')), SameSide(Point('A'),Point('C'),Point('B'),Point('M')), SameSide(Point('A'),Point('C'),Point('B'),Point('P')), SameSide(Point('M'),Point('P'),Point('A'),Point('B')), SameSide(Point('M'),Point('P'),Point('B'),Point('C')), SameSide(Point('C'),Point('M'),Point('A'),Point('P')), NotCollinear(Point('B'),Point('C'),Point('M')), SameSide(Point('C'),Point('P'),Point('A'),Point('B')), NotCollinear(Point('B'),Point('C'),Point('P')), SameSide(Point('A'),Point('C'),Point('M'),Point('P')), OppositeSide(Point('A'),Point('M'),Point('C'),Point('P')), OppositeSide(Point('B'),Point('C'),Point('A'),Point('P')), OppositeSide(Point('A'),Point('P'),Point('B'),Point('C')), NotCollinear(Point('A'),Point('B'),Point('C')), SameSide(Point('B'),Point('P'),Point('A'),Point('C')), SameSide(Point('B'),Point('P'),Point('A'),Point('M')), OppositeSide(Point('A'),Point('M'),Point('B'),Point('C')), OppositeSide(Point('B'),Point('M'),Point('C'),Point('P')), NotCollinear(Point('A'),Point('C'),Point('P'))}
