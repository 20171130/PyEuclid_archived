import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('E'),Point('G')) - (Variable('y') + sympy.simplify('4'))), (Length(Point('F'),Point('G')) - sympy.simplify('15')), (Length(Point('E'),Point('F')) - sympy.simplify('12')), (Length(Point('B'),Point('C')) - sympy.simplify('20')), (Length(Point('A'),Point('B')) - (sympy.simplify('2') * Variable('x'))), (Length(Point('A'),Point('C')) - sympy.simplify('12')), (Angle(Point('B'),Point('A'),Point('C')) - Angle(Point('F'),Point('E'),Point('G'))), (Angle(Point('A'),Point('B'),Point('C')) - Angle(Point('E'),Point('F'),Point('G'))), (Angle(Point('A'),Point('C'),Point('B')) - Angle(Point('E'),Point('G'),Point('F'))), Similar(Point('A'),Point('C'),Point('B'),Point('E'),Point('G'),Point('F'))]
goal = Variable('y')
solution = '5'

diagrammatic_relations = [NotCollinear(Point('A'),Point('B'),Point('C'))]
