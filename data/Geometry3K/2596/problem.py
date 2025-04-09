import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('K'),Point('L')) - (sympy.simplify('4') * Variable('x'))), (Length(Point('J'),Point('L')) - ((sympy.simplify('5') * Variable('x')) - sympy.simplify('6'))), (Length(Point('J'),Point('K')) - ((sympy.simplify('3') * Variable('x')) + sympy.simplify('6'))), (Length(Point('K'),Point('L')) - Length(Point('J'),Point('K'))), (Length(Point('J'),Point('K')) - Length(Point('J'),Point('L')))]
goal = Variable('x')
solution = '6'

diagrammatic_relations = [NotCollinear(Point('J'),Point('K'),Point('L'))]

new_diagrammatic_relations = {NotCollinear(Point('J'),Point('K'),Point('L'))}

