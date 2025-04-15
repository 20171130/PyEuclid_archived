import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('B'),Point('C')) - Variable('x')), (Length(Point('A'),Point('X')) - (sympy.simplify('2') * Variable('x'))), (Area(Point('A'),Point('B'),Point('X'),Point('C')) - sympy.simplify('169')), Rhombus(Point('A'),Point('B'),Point('X'),Point('C'))]
goal = Length(Point('A'),Point('X'))
solution = '26'

diagrammatic_relations = [NotCollinear(Point('B'),Point('C'),Point('X')), NotCollinear(Point('A'),Point('C'),Point('X')), SameSide(Point('A'),Point('B'),Point('C'),Point('X')), OppositeSide(Point('A'),Point('X'),Point('B'),Point('C')), SameSide(Point('B'),Point('X'),Point('A'),Point('C')), OppositeSide(Point('B'),Point('C'),Point('A'),Point('X')), SameSide(Point('C'),Point('X'),Point('A'),Point('B')), NotCollinear(Point('A'),Point('B'),Point('C')), NotCollinear(Point('A'),Point('B'),Point('X')), SameSide(Point('A'),Point('C'),Point('B'),Point('X'))]

new_diagrammatic_relations = {SameSide(Point('A'),Point('C'),Point('B'),Point('X')), OppositeSide(Point('A'),Point('X'),Point('B'),Point('C')), NotCollinear(Point('A'),Point('C'),Point('X')), SameSide(Point('A'),Point('B'),Point('C'),Point('X')), NotCollinear(Point('B'),Point('C'),Point('X')), NotCollinear(Point('A'),Point('B'),Point('X')), OppositeSide(Point('B'),Point('C'),Point('A'),Point('X')), SameSide(Point('C'),Point('X'),Point('A'),Point('B')), NotCollinear(Point('A'),Point('B'),Point('C')), SameSide(Point('B'),Point('X'),Point('A'),Point('C'))}

