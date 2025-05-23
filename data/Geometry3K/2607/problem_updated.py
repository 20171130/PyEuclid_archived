import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('B'),Point('E')) - sympy.simplify('5')), (Length(Point('B'),Point('C')) - ((sympy.simplify('2') * Variable('x')) - sympy.simplify('8'))), (Length(Point('B'),Point('D')) - sympy.simplify('3')), (Length(Point('A'),Point('B')) - (Variable('x') + sympy.simplify('3'))), Between(Point('B'),Point('D'),Point('E')), Collinear(Point('B'),Point('D'),Point('E')), Between(Point('B'),Point('A'),Point('C')), Collinear(Point('A'),Point('B'),Point('C')), Parallel(Point('A'),Point('E'),Point('C'),Point('D'))]
goal = Length(Point('B'),Point('C'))
solution = '6'

diagrammatic_relations = {NotCollinear(Point('A'),Point('D'),Point('E')), NotCollinear(Point('B'),Point('C'),Point('D')), OppositeSide(Point('A'),Point('C'),Point('D'),Point('E')), NotCollinear(Point('B'),Point('C'),Point('E')), SameSide(Point('A'),Point('D'),Point('C'),Point('E')), NotCollinear(Point('C'),Point('D'),Point('E')), SameSide(Point('A'),Point('B'),Point('C'),Point('D')), SameSide(Point('B'),Point('D'),Point('C'),Point('E')), OppositeSide(Point('A'),Point('C'),Point('B'),Point('E')), SameSide(Point('B'),Point('E'),Point('A'),Point('D')), SameSide(Point('B'),Point('D'),Point('A'),Point('E')), SameSide(Point('A'),Point('B'),Point('C'),Point('E')), OppositeSide(Point('D'),Point('E'),Point('A'),Point('B')), SameSide(Point('B'),Point('E'),Point('C'),Point('D')), SameSide(Point('B'),Point('C'),Point('A'),Point('E')), Between(Point('B'),Point('A'),Point('C')), Between(Point('B'),Point('D'),Point('E')), SameSide(Point('A'),Point('E'),Point('C'),Point('D')), NotCollinear(Point('A'),Point('C'),Point('E')), OppositeSide(Point('D'),Point('E'),Point('B'),Point('C')), SameSide(Point('C'),Point('D'),Point('A'),Point('E')), NotCollinear(Point('A'),Point('C'),Point('D')), SameSide(Point('B'),Point('C'),Point('A'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('D')), OppositeSide(Point('A'),Point('C'),Point('B'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('E')), SameSide(Point('C'),Point('E'),Point('A'),Point('D')), OppositeSide(Point('D'),Point('E'),Point('A'),Point('C'))}
