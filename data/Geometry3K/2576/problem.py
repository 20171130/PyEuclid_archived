import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('X'),Point('Y')) - ((sympy.simplify('2') * Variable('x')) + sympy.simplify('3'))), (Length(Point('X'),Point('Z')) - ((sympy.simplify('8') * Variable('x')) - sympy.simplify('4'))), (Length(Point('Y'),Point('Z')) - ((sympy.simplify('4') * Variable('x')) - sympy.simplify('1'))), (Length(Point('Y'),Point('Z')) - Length(Point('X'),Point('Y'))), (Length(Point('X'),Point('Y')) - Length(Point('Y'),Point('Z'))), (Length(Point('X'),Point('Y')) - Length(Point('Y'),Point('Z')))]
goal = Length(Point('X'),Point('Y'))
solution = '7'

diagrammatic_relations = [NotCollinear(Point('X'),Point('Y'),Point('Z'))]

new_diagrammatic_relations = {NotCollinear(Point('X'),Point('Y'),Point('Z'))}

