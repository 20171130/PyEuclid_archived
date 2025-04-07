import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


relations = [(Length(Point('M'),Point('N')) - ((sympy.simplify('4') * Variable('x')) - sympy.simplify('2'))), (Length(Point('L'),Point('M')) - ((sympy.simplify('3') * Variable('x')) + sympy.simplify('1'))), (Angle(Point('L'),Point('P'),Point('M')) - (((sympy.simplify('5') * Variable('y')) / sympy.simplify('180')) * sympy.simplify('pi'))), Between(Point('P'),Point('L'),Point('N')), Collinear(Point('L'),Point('N'),Point('P')), (Length(Point('L'),Point('M')) - Length(Point('M'),Point('N'))), (Length(Point('M'),Point('N')) - Length(Point('L'),Point('N'))), (Length(Point('L'),Point('N')) - Length(Point('L'),Point('M'))), (Angle(Point('L'),Point('M'),Point('P')) - Angle(Point('N'),Point('M'),Point('P'))), (Length(Point('L'),Point('M')) - Length(Point('M'),Point('N'))), (Length(Point('M'),Point('N')) - Length(Point('L'),Point('N'))), (Length(Point('L'),Point('N')) - Length(Point('L'),Point('M'))), (Angle(Point('L'),Point('M'),Point('P')) - Angle(Point('N'),Point('M'),Point('P')))]
goal = Length(Point('L'),Point('M'))
solution = '10'

diagrammatic_relations = {NotCollinear(Point('L'),Point('M'),Point('P')), NotCollinear(Point('M'),Point('N'),Point('P')), OppositeSide(Point('L'),Point('N'),Point('M'),Point('P')), NotCollinear(Point('L'),Point('M'),Point('N')), SameSide(Point('L'),Point('P'),Point('M'),Point('N')), SameSide(Point('N'),Point('P'),Point('L'),Point('M'))}
