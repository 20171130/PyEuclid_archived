import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('A'),Point('C')) - sympy.simplify('7')), (Length(Point('A'),Point('B')) - (sympy.simplify('3') * Variable('x'))), (((Length(Point('A'),Point('B')) + Length(Point('B'),Point('C'))) + Length(Point('A'),Point('C'))) - sympy.simplify('25')), (((Length(Point('A'),Point('B')) + Length(Point('B'),Point('C'))) + Length(Point('A'),Point('C'))) - sympy.simplify('25')), (Length(Point('C'),Point('E')) - Variable('radius_E')), (Length(Point('A'),Point('E')) - Variable('radius_E')), (Angle(Point('B'),Point('A'),Point('E')) - sympy.simplify('pi/2')), (Angle(Point('B'),Point('C'),Point('E')) - sympy.simplify('pi/2'))]
goal = Variable('x')
solution = '3'

diagrammatic_relations = [SameSide(Point('A'),Point('B'),Point('C'),Point('E')), NotCollinear(Point('A'),Point('B'),Point('C')), NotCollinear(Point('A'),Point('B'),Point('E')), OppositeSide(Point('A'),Point('C'),Point('B'),Point('E')), NotCollinear(Point('A'),Point('C'),Point('E')), SameSide(Point('C'),Point('E'),Point('A'),Point('B')), NotCollinear(Point('B'),Point('C'),Point('E')), OppositeSide(Point('B'),Point('E'),Point('A'),Point('C')), SameSide(Point('A'),Point('E'),Point('B'),Point('C')), SameSide(Point('B'),Point('C'),Point('A'),Point('E'))]

new_diagrammatic_relations = {OppositeSide(Point('B'),Point('E'),Point('A'),Point('C')), SameSide(Point('B'),Point('C'),Point('A'),Point('E')), SameSide(Point('C'),Point('E'),Point('A'),Point('B')), NotCollinear(Point('A'),Point('B'),Point('E')), NotCollinear(Point('B'),Point('C'),Point('E')), NotCollinear(Point('A'),Point('C'),Point('E')), NotCollinear(Point('A'),Point('B'),Point('C')), SameSide(Point('A'),Point('E'),Point('B'),Point('C')), OppositeSide(Point('A'),Point('C'),Point('B'),Point('E')), SameSide(Point('A'),Point('B'),Point('C'),Point('E'))}

