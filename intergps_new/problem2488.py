import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


relations = [(Length(Point('F'),Point('W')) - sympy.simplify('12')), (Length(Point('F'),Point('Wprime')) - Variable('x')), (Length(Point('W'),Point('Wprime')) - sympy.simplify('8')), Between(Point('Wprime'),Point('F'),Point('W')), Collinear(Point('F'),Point('W'),Point('Wprime'))]
goal = (Length(Point('F'),Point('Wprime')) / Length(Point('F'),Point('W')))
solution = '(1)/(3)'

diagrammatic_relations = {NotCollinear(Point('A'),Point('B'),Point('W'))}
