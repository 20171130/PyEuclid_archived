import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [Between(Point('C'),Point('A'),Point('E')), Collinear(Point('C'),Point('A'),Point('E')), Length(Point('A'),Point('E'))-15, Between(Point('C'),Point('A'),Point('G')), Collinear(Point('C'),Point('A'),Point('G')),Length(Point('C'),Point('G'))-5/2, Length(Point('A'), Point('C'))-Length(Point('C'), Point('E')), Length(Point('F'), Point('C'))-Length(Point('C'), Point('G'))]
goal = (Length(Point('C'),Point('E')) ** 2 * sympy.simplify('pi') - sympy.simplify('3') * Length(Point('C'),Point('G')) ** 2 * sympy.simplify('pi'))/2
solution = '58.9'

diagrammatic_relations = set()