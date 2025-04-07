import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


relations = [(Length(Point('B'),Point('C')) - sympy.simplify('17/2')), (Length(Point('A'),Point('B')) - Variable('z')), (Length(Point('C'),Point('D')) - Variable('x')), (Length(Point('A'),Point('D')) - sympy.simplify('88/10')), (Length(Point('B'),Point('D')) - Variable('y')), Between(Point('D'),Point('A'),Point('C')), Collinear(Point('A'),Point('C'),Point('D')), Perpendicular(Point('A'),Point('D'),Point('B'),Point('D')), Perpendicular(Point('A'),Point('B'),Point('B'),Point('C'))]
goal = Variable('x')
solution = '5.17'

diagrammatic_relations = {NotCollinear(Point('A'),Point('B'),Point('C')), SameSide(Point('A'),Point('D'),Point('B'),Point('C')), 
                    NotCollinear(Point('A'),Point('B'),Point('D')), SameSide(Point('C'),Point('D'),Point('A'),Point('B')), 
                    OppositeSide(Point('A'),Point('C'),Point('B'),Point('D')), NotCollinear(Point('B'),Point('C'),Point('D')),
                    }
