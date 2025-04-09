import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('B'),Point('C')) - ( Variable('x') * 3)), (Length(Point('B'),Point('X')) - 8), Between(Point('X'),Point('A'),Point('C')), Collinear(Point('A'),Point('C'),Point('X')), (Length(Point('A'),Point('X')) - Length(Point('C'),Point('X'))), (Length(Point('F'),Point('H')) - Variable('x')), (Length(Point('F'),Point('G')) - 6), Between(Point('H'),Point('E'),Point('G')), Collinear(Point('E'),Point('G'),Point('H')), (Length(Point('G'),Point('H')) - Length(Point('E'),Point('H'))), (Angle(Point('B'),Point('C'),Point('X')) - Angle(Point('F'),Point('G'),Point('H'))), (Angle(Point('B'),Point('A'),Point('X')) - Angle(Point('F'),Point('E'),Point('H')))]
goal = Variable('x')
solution = '4'

diagrammatic_relations = [OppositeSide(Point('A'),Point('C'),Point('B'),Point('X')), 
                    SameSide(Point('C'),Point('X'),Point('A'),Point('B')), 
                    NotCollinear(Point('A'),Point('B'),Point('C')), NotCollinear(Point('B'),Point('C'),Point('X')), 
                    SameSide(Point('A'),Point('X'),Point('B'),Point('C')), NotCollinear(Point('A'),Point('B'),Point('X')),
                    OppositeSide(Point('G'),Point('E'),Point('F'),Point('H')),
                    NotCollinear(Point('E'),Point('F'),Point('G'))]

new_diagrammatic_relations = {Between(Point('X'),Point('A'),Point('C')), NotCollinear(Point('B'),Point('C'),Point('X')), SameSide(Point('A'),Point('X'),Point('B'),Point('C')), NotCollinear(Point('A'),Point('B'),Point('X')), SameSide(Point('C'),Point('X'),Point('A'),Point('B')), NotCollinear(Point('A'),Point('B'),Point('C')), OppositeSide(Point('A'),Point('C'),Point('B'),Point('X'))}

