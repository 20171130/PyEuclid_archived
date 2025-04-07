import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


relations = [Between(Point('Q'),Point('D'),Point('X')), Collinear(Point('D'),Point('Q'),Point('X')), Between(Point('D'),Point('T'),Point('X')), Collinear(Point('D'),Point('T'),Point('X')), Between(Point('Q'),Point('T'),Point('X')), Collinear(Point('Q'),Point('T'),Point('X')), Between(Point('D'),Point('Q'),Point('T')), Collinear(Point('D'),Point('Q'),Point('T')), Perpendicular(Point('D'),Point('E'),Point('E'),Point('X')), Perpendicular(Point('A'),Point('D'),Point('A'),Point('X')), (Length(Point('E'),Point('X')) - sympy.simplify('24')),(Length(Point('A'),Point('X')) - sympy.simplify('24')), (Length(Point('D'),Point('E')) - sympy.simplify('7')),  (Length(Point('A'),Point('D')) - Variable('radius_D')), (Length(Point('D'),Point('E')) - Variable('radius_D')), (Length(Point('D'),Point('T')) - Variable('radius_D')), (Length(Point('D'),Point('Q')) - Variable('radius_D'))]
goal = Length(Point('T'),Point('X'))
solution = '32'

diagrammatic_relations = {Not(Collinear(Point('A'),Point('D'),Point('X')))}