import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [Rhombus(Point('A'),Point('B'),Point('C'),Point('D')), (Length(Point('A'),Point('B')) - ((sympy.simplify('2') * Variable('x')) + sympy.simplify('3'))), (Length(Point('B'),Point('C')) - (Variable('x') + sympy.simplify('7'))), Rhombus(Point('A'),Point('B'),Point('C'),Point('D')), (Length(Point('A'),Point('B')) - ((sympy.simplify('2') * Variable('x')) + sympy.simplify('3'))), (Length(Point('B'),Point('C')) - (Variable('x') + sympy.simplify('7')))]
goal = Length(Point('C'),Point('D'))
solution = '11'

diagrammatic_relations = [SameSide(Point('A'),Point('B'),Point('C'),Point('D')), NotCollinear(Point('A'),Point('C'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('C')), SameSide(Point('A'),Point('D'),Point('B'),Point('C')), NotCollinear(Point('A'),Point('B'),Point('D')), SameSide(Point('C'),Point('D'),Point('A'),Point('B')), OppositeSide(Point('A'),Point('C'),Point('B'),Point('D')), SameSide(Point('B'),Point('C'),Point('A'),Point('D')), NotCollinear(Point('B'),Point('C'),Point('D')), OppositeSide(Point('B'),Point('D'),Point('A'),Point('C'))]

new_diagrammatic_relations = {SameSide(Point('C'),Point('D'),Point('A'),Point('B')), SameSide(Point('B'),Point('C'),Point('A'),Point('D')), NotCollinear(Point('B'),Point('C'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('D')), OppositeSide(Point('A'),Point('C'),Point('B'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('C')), SameSide(Point('A'),Point('B'),Point('C'),Point('D')), SameSide(Point('A'),Point('D'),Point('B'),Point('C')), OppositeSide(Point('B'),Point('D'),Point('A'),Point('C')), NotCollinear(Point('A'),Point('C'),Point('D'))}

