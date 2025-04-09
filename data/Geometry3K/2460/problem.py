import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('A'),Point('C')) - sympy.simplify('29')), (Angle(Point('A'),Point('C'),Point('B')) - ((Variable('x') / sympy.simplify('180')) * sympy.simplify('pi'))), (Length(Point('A'),Point('B')) - sympy.simplify('61')), (Length(Point('B'),Point('C')) - sympy.simplify('50'))]
goal = Variable('x')
solution = '98'

diagrammatic_relations = [NotCollinear(Point('A'),Point('B'),Point('C'))]

new_diagrammatic_relations = {NotCollinear(Point('A'),Point('B'),Point('C'))}

