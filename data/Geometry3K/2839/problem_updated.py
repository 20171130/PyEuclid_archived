import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [Between(Point('K'),Point('J'),Point('L')), Collinear(Point('J'),Point('K'),Point('L')), (Length(Point('J'),Point('L')) - Variable('x')), (Angle(Point('J'),Point('K'),Point('L')) - sympy.simplify('180/180*pi')), (Length(Point('K'),Point('L')) - (sympy.simplify(sympy.sqrt(132)) / sympy.simplify('sqrt(pi)'))), (Length(Point('J'),Point('K')) - (sympy.simplify(sympy.sqrt(132)) / sympy.simplify('sqrt(pi)')))]
goal = Variable('x')
solution = '13.0'

diagrammatic_relations = {Between(Point('K'),Point('J'),Point('L'))}
