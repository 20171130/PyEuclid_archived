import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('J'),Point('K')) - (Variable('x') + sympy.simplify('7'))), (Length(Point('J'),Point('L')) - ((sympy.simplify('4') * Variable('x')) - sympy.simplify('8'))), (Length(Point('J'),Point('K')) - Length(Point('J'),Point('L'))), (Length(Point('J'),Point('K')) - Length(Point('K'),Point('L'))), (Length(Point('K'),Point('L')) - Length(Point('J'),Point('L')))]
goal = Length(Point('K'),Point('L'))
solution = '12'

diagrammatic_relations = [NotCollinear(Point('J'),Point('K'),Point('L'))]

new_diagrammatic_relations = {NotCollinear(Point('J'),Point('K'),Point('L'))}

