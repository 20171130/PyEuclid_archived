import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('A'),Point('C')) - (sympy.simplify('73.8000000000000') * Variable('x'))), (Length(Point('A'),Point('B')) - ((sympy.simplify('150') * Variable('x')) + sympy.simplify('91'))), (Length(Point('B'),Point('C')) - ((sympy.simplify('110') * Variable('x')) + sympy.simplify('53'))), (((Length(Point('A'),Point('B')) + Length(Point('B'),Point('C'))) + Length(Point('A'),Point('C'))) - sympy.simplify('3482')), (((Length(Point('A'),Point('B')) + Length(Point('B'),Point('C'))) + Length(Point('A'),Point('C'))) - sympy.simplify('3482'))]
goal = Length(Point('A'),Point('B'))
solution = '1591'

diagrammatic_relations = [NotCollinear(Point('A'),Point('B'),Point('C'))]
