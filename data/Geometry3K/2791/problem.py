import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('J'),Point('K')) - Variable('a')), Between(Point('G'),Point('F'),Point('H')), Collinear(Point('F'),Point('G'),Point('H')), Between(Point('K'),Point('F'),Point('J')), Collinear(Point('F'),Point('J'),Point('K')), (Length(Point('F'),Point('G')) - sympy.simplify('18')), (Length(Point('G'),Point('H')) - sympy.simplify('42')), (Length(Point('F'),Point('K')) - sympy.simplify('15')), (Length(Point('F'),Point('G')) - sympy.simplify('18')), (Length(Point('G'),Point('H')) - sympy.simplify('42')), (Length(Point('F'),Point('K')) - sympy.simplify('15')), (Length(Point('A'),Point('H')) - Variable('radius_A')), (Length(Point('A'),Point('J')) - Variable('radius_A')), (Length(Point('A'),Point('K')) - Variable('radius_A')), (Length(Point('A'),Point('G')) - Variable('radius_A'))]
goal = Variable('a')
solution = '57'

diagrammatic_relations = set()