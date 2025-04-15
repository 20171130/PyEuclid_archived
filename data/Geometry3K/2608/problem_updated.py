import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('M'),Point('N')) - ((sympy.simplify('4') * Variable('x')) - sympy.simplify('2'))), (Length(Point('L'),Point('M')) - ((sympy.simplify('3') * Variable('x')) + sympy.simplify('1'))), (Angle(Point('L'),Point('P'),Point('M')) - (((sympy.simplify('5') * Variable('y')) / sympy.simplify('180')) * sympy.simplify('pi'))), Between(Point('P'),Point('L'),Point('N')), Collinear(Point('L'),Point('N'),Point('P')), (Length(Point('L'),Point('M')) - Length(Point('M'),Point('N'))), (Length(Point('M'),Point('N')) - Length(Point('L'),Point('N'))), (Length(Point('L'),Point('N')) - Length(Point('L'),Point('M'))), (Angle(Point('L'),Point('M'),Point('P')) - Angle(Point('N'),Point('M'),Point('P'))), (Length(Point('L'),Point('M')) - Length(Point('M'),Point('N'))), (Length(Point('M'),Point('N')) - Length(Point('L'),Point('N'))), (Length(Point('L'),Point('N')) - Length(Point('L'),Point('M'))), (Angle(Point('L'),Point('M'),Point('P')) - Angle(Point('N'),Point('M'),Point('P')))]
goal = Variable('y')
solution = '18'

diagrammatic_relations = {SameSide(Point('N'),Point('P'),Point('L'),Point('M')), SameSide(Point('L'),Point('P'),Point('M'),Point('N')), NotCollinear(Point('L'),Point('M'),Point('N')), OppositeSide(Point('L'),Point('N'),Point('M'),Point('P')), NotCollinear(Point('L'),Point('M'),Point('P')), Between(Point('P'),Point('L'),Point('N')), NotCollinear(Point('M'),Point('N'),Point('P'))}
