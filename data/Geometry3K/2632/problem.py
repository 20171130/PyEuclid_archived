import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [Between(Point('G'),Point('A'),Point('C')), Collinear(Point('A'),Point('C'),Point('G')), Between(Point('H'),Point('D'),Point('F')), Collinear(Point('D'),Point('F'),Point('H')), Similar(Point('A'),Point('B'),Point('C'),Point('D'),Point('E'),Point('F')), Midpoint(Point('G'),Point('A'),Point('C')), Midpoint(Point('H'),Point('D'),Point('F')), (Length(Point('B'),Point('C')) - sympy.simplify('30')), (Length(Point('B'),Point('G')) - sympy.simplify('15')), (Length(Point('E'),Point('F')) - sympy.simplify('15')), Similar(Point('A'),Point('B'),Point('C'),Point('D'),Point('E'),Point('F')), Midpoint(Point('G'),Point('A'),Point('C')), Midpoint(Point('H'),Point('D'),Point('F')), (Length(Point('B'),Point('C')) - sympy.simplify('30')), (Length(Point('B'),Point('G')) - sympy.simplify('15')), (Length(Point('E'),Point('F')) - sympy.simplify('15'))]
goal = Length(Point('E'),Point('H'))
solution = '7.5'

diagrammatic_relations = [NotCollinear(Point('A'),Point('B'),Point('C')), NotCollinear(Point('B'),Point('C'),Point('G')), SameSide(Point('A'),Point('G'),Point('B'),Point('C')),SameSide(Point('D'),Point('H'),Point('E'),Point('F')), OppositeSide(Point('D'),Point('F'),Point('E'),Point('H')), OppositeSide(Point('A'),Point('C'),Point('B'),Point('G')), NotCollinear(Point('A'),Point('B'),Point('G')), SameSide(Point('C'),Point('G'),Point('A'),Point('B'))]
new_diagrammatic_relations = {NotCollinear(Point('A'),Point('B'),Point('C')), NotCollinear(Point('B'),Point('C'),Point('G')), SameSide(Point('A'),Point('G'),Point('B'),Point('C')),SameSide(Point('D'),Point('H'),Point('E'),Point('F')), OppositeSide(Point('D'),Point('F'),Point('E'),Point('H')), OppositeSide(Point('A'),Point('C'),Point('B'),Point('G')), NotCollinear(Point('A'),Point('B'),Point('G')), SameSide(Point('C'),Point('G'),Point('A'),Point('B'))}

