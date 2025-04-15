import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('B'),Point('C')) - ((sympy.simplify('4') * Variable('y')) - sympy.simplify('5'))), (Angle(Point('B'),Point('A'),Point('C')) - (((sympy.simplify('2') * Variable('x')) / sympy.simplify('180')) * sympy.simplify('pi'))), (Length(Point('A'),Point('B')) - sympy.simplify('3')), (Angle(Point('A'),Point('B'),Point('C')) - (((sympy.simplify('2') * Variable('x')) / sympy.simplify('180')) * sympy.simplify('pi'))), (Length(Point('A'),Point('C')) - Length(Point('A'),Point('B')))]
goal = Variable('x')
solution = '30'

diagrammatic_relations = [NotCollinear(Point('A'),Point('B'),Point('C'))]

new_diagrammatic_relations = {NotCollinear(Point('A'),Point('B'),Point('C'))}

