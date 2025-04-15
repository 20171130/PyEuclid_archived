import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [Between(Point('N'),Point('K'),Point('L')), Collinear(Point('K'),Point('L'),Point('N')), Between(Point('Q'),Point('P'),Point('R')), Collinear(Point('P'),Point('Q'),Point('R')), Between(Point('R'),Point('L'),Point('M')), Collinear(Point('L'),Point('M'),Point('R')), Between(Point('P'),Point('K'),Point('M')), Collinear(Point('K'),Point('M'),Point('P')), Perpendicular(Point('M'),Point('P'),Point('M'),Point('R')), Perpendicular(Point('K'),Point('N'),Point('N'),Point('Q')), Parallel(Point('K'),Point('L'),Point('P'),Point('R')), (Length(Point('K'),Point('N')) - sympy.simplify('9')), (Length(Point('L'),Point('N')) - sympy.simplify('16')), (Length(Point('M'),Point('P')) - (Length(Point('K'),Point('P')) * sympy.simplify('2'))), Parallel(Point('K'),Point('L'),Point('P'),Point('R')), (Length(Point('K'),Point('N')) - sympy.simplify('9')), (Length(Point('L'),Point('N')) - sympy.simplify('16')), (Length(Point('M'),Point('P')) - (Length(Point('K'),Point('P')) * sympy.simplify('2')))]
goal = Length(Point('K'),Point('M'))
solution = '15'

diagrammatic_relations = set()
