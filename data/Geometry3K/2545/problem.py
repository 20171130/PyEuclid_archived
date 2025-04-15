import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [Between(Point('C'),Point('A'),Point('E')), Collinear(Point('C'),Point('A'),Point('E')), Length(Point('A'),Point('E'))-15, Between(Point('C'),Point('A'),Point('G')), Collinear(Point('C'),Point('A'),Point('G')),Length(Point('C'),Point('G'))-5/2, Length(Point('A'), Point('C'))-Length(Point('C'), Point('E')), Length(Point('F'), Point('C'))-Length(Point('C'), Point('G'))]
goal = (Length(Point('C'),Point('E')) ** 2 * sympy.simplify('pi') - sympy.simplify('3') * Length(Point('C'),Point('G')) ** 2 * sympy.simplify('pi'))/2
solution = '58.9'

diagrammatic_relations = set()
new_diagrammatic_relations = {SameSide(Point('A'),Point('C'),Point('F'),Point('G')), SameSide(Point('C'),Point('E'),Point('A'),Point('F')), Between(Point('C'),Point('A'),Point('G')), NotCollinear(Point('C'),Point('E'),Point('F')), Between(Point('E'),Point('C'),Point('G')), OppositeSide(Point('A'),Point('G'),Point('C'),Point('F')), OppositeSide(Point('A'),Point('E'),Point('F'),Point('G')), OppositeSide(Point('C'),Point('E'),Point('F'),Point('G')), SameSide(Point('A'),Point('G'),Point('E'),Point('F')), NotCollinear(Point('E'),Point('F'),Point('G')), SameSide(Point('E'),Point('G'),Point('A'),Point('F')), NotCollinear(Point('A'),Point('C'),Point('F')), NotCollinear(Point('A'),Point('F'),Point('G')), Between(Point('E'),Point('A'),Point('G')), NotCollinear(Point('A'),Point('E'),Point('F')), SameSide(Point('A'),Point('C'),Point('E'),Point('F')), SameSide(Point('E'),Point('G'),Point('C'),Point('F')), SameSide(Point('C'),Point('G'),Point('A'),Point('F')), Between(Point('C'),Point('A'),Point('E')), OppositeSide(Point('A'),Point('E'),Point('C'),Point('F')), NotCollinear(Point('C'),Point('F'),Point('G')), SameSide(Point('C'),Point('G'),Point('E'),Point('F'))}

