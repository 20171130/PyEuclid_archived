import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('C'),Point('D')) - sympy.simplify('6')), (Length(Point('C'),Point('E')) - (sympy.simplify('12') - Variable('x'))), (Length(Point('A'),Point('C')) - (Variable('x') + sympy.simplify('7'))), (Length(Point('B'),Point('C')) - sympy.simplify('4')), Between(Point('C'),Point('B'),Point('D')), Collinear(Point('B'),Point('C'),Point('D')), Between(Point('C'),Point('A'),Point('E')), Collinear(Point('A'),Point('C'),Point('E')), Perpendicular(Point('A'),Point('B'),Point('B'),Point('D')), Perpendicular(Point('B'),Point('D'),Point('D'),Point('E')), Similar(Point('A'),Point('B'),Point('C'),Point('E'),Point('D'),Point('C'))]
goal = Length(Point('A'),Point('C'))
solution = '7.6'

diagrammatic_relations = [SameSide(Point('C'),Point('D'),Point('B'),Point('E')), SameSide(Point('A'),Point('C'),Point('D'),Point('E')), NotCollinear(Point('A'),Point('B'),Point('E')), OppositeSide(Point('A'),Point('E'),Point('C'),Point('D')), SameSide(Point('A'),Point('B'),Point('D'),Point('E')), SameSide(Point('C'),Point('D'),Point('A'),Point('B')), OppositeSide(Point('A'),Point('E'),Point('B'),Point('D')), SameSide(Point('B'),Point('E'),Point('A'),Point('D')), OppositeSide(Point('B'),Point('D'),Point('A'),Point('E')), SameSide(Point('D'),Point('E'),Point('A'),Point('B')), SameSide(Point('C'),Point('E'),Point('A'),Point('B')), SameSide(Point('A'),Point('D'),Point('B'),Point('E')), SameSide(Point('B'),Point('C'),Point('D'),Point('E')), OppositeSide(Point('B'),Point('D'),Point('A'),Point('C')), SameSide(Point('A'),Point('C'),Point('B'),Point('E')), NotCollinear(Point('A'),Point('B'),Point('D')), NotCollinear(Point('B'),Point('C'),Point('E')), NotCollinear(Point('C'),Point('D'),Point('E')), SameSide(Point('B'),Point('C'),Point('A'),Point('D')), NotCollinear(Point('A'),Point('C'),Point('D')), SameSide(Point('C'),Point('E'),Point('A'),Point('D')), OppositeSide(Point('B'),Point('D'),Point('C'),Point('E')), NotCollinear(Point('A'),Point('B'),Point('C')), OppositeSide(Point('A'),Point('E'),Point('B'),Point('C')), NotCollinear(Point('A'),Point('D'),Point('E')), NotCollinear(Point('B'),Point('D'),Point('E'))]
