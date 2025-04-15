import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('C'),Point('D')) - sympy.simplify('5')), (Length(Point('A'),Point('B')) - sympy.simplify('2')), (Length(Point('A'),Point('E')) - (Variable('x') - sympy.simplify('1'))), (Length(Point('D'),Point('E')) - (Variable('x') + sympy.simplify('5'))), Between(Point('E'),Point('B'),Point('C')), Collinear(Point('B'),Point('C'),Point('E')), Between(Point('E'),Point('A'),Point('D')), Collinear(Point('A'),Point('D'),Point('E')), Parallel(Point('A'),Point('B'),Point('C'),Point('D'))]
goal = Length(Point('D'),Point('E'))
solution = '10'

diagrammatic_relations = {OppositeSide(Point('A'),Point('D'),Point('B'),Point('C')), NotCollinear(Point('B'),Point('C'),Point('D')), SameSide(Point('D'),Point('E'),Point('A'),Point('C')), OppositeSide(Point('B'),Point('C'),Point('D'),Point('E')), Between(Point('E'),Point('B'),Point('C')), NotCollinear(Point('B'),Point('D'),Point('E')), OppositeSide(Point('A'),Point('D'),Point('C'),Point('E')), SameSide(Point('B'),Point('D'),Point('A'),Point('C')), NotCollinear(Point('C'),Point('D'),Point('E')), SameSide(Point('C'),Point('D'),Point('A'),Point('B')), SameSide(Point('A'),Point('C'),Point('B'),Point('D')), SameSide(Point('A'),Point('B'),Point('C'),Point('D')), SameSide(Point('B'),Point('E'),Point('C'),Point('D')), OppositeSide(Point('B'),Point('C'),Point('A'),Point('D')), SameSide(Point('D'),Point('E'),Point('A'),Point('B')), SameSide(Point('C'),Point('E'),Point('A'),Point('B')), SameSide(Point('A'),Point('E'),Point('C'),Point('D')), NotCollinear(Point('A'),Point('C'),Point('E')), OppositeSide(Point('B'),Point('C'),Point('A'),Point('E')), NotCollinear(Point('A'),Point('C'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('E')), Between(Point('E'),Point('A'),Point('D')), SameSide(Point('A'),Point('E'),Point('B'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('C')), OppositeSide(Point('A'),Point('D'),Point('B'),Point('E')), SameSide(Point('B'),Point('E'),Point('A'),Point('C')), SameSide(Point('C'),Point('E'),Point('B'),Point('D'))}
