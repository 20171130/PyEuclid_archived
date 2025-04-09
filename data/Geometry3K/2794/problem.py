import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('A'),Point('B')) - Variable('x')), (Length(Point('E'),Point('F')) - sympy.simplify('4')), (Area(Point('A'),Point('B'),Point('D'),Point('C')) - sympy.simplify('32')), Quadrilateral(Point('A'),Point('B'),Point('D'),Point('C')), (Area(Point('E'),Point('F'),Point('G'),Point('H')) - sympy.simplify('8')), Quadrilateral(Point('E'),Point('F'),Point('G'),Point('H')), Quadrilateral(Point('A'),Point('B'),Point('D'),Point('C')), Quadrilateral(Point('E'),Point('F'),Point('G'),Point('H')), Similar4P(Point('A'),Point('B'),Point('D'),Point('C'),Point('E'),Point('F'),Point('G'),Point('H'))]
goal = (Length(Point('E'),Point('F')) / Length(Point('A'),Point('B')))
solution = '(1)/(2)'

diagrammatic_relations = [SameSide(Point('A'),Point('B'),Point('C'),Point('D')), NotCollinear(Point('A'),Point('C'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('C')), NotCollinear(Point('A'),Point('B'),Point('D')), SameSide(Point('C'),Point('D'),Point('A'),Point('B')), NotCollinear(Point('B'),Point('C'),Point('D')), SameSide(Point('A'),Point('C'),Point('B'),Point('D')), OppositeSide(Point('A'),Point('D'),Point('B'),Point('C')), OppositeSide(Point('B'),Point('C'),Point('A'),Point('D')), SameSide(Point('B'),Point('D'),Point('A'),Point('C'))]

new_diagrammatic_relations = {SameSide(Point('B'),Point('D'),Point('A'),Point('C')), SameSide(Point('C'),Point('D'),Point('A'),Point('B')), OppositeSide(Point('A'),Point('D'),Point('B'),Point('C')), NotCollinear(Point('B'),Point('C'),Point('D')), OppositeSide(Point('B'),Point('C'),Point('A'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('D')), NotCollinear(Point('A'),Point('B'),Point('C')), SameSide(Point('A'),Point('C'),Point('B'),Point('D')), SameSide(Point('A'),Point('B'),Point('C'),Point('D')), NotCollinear(Point('A'),Point('C'),Point('D'))}

