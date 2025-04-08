import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Angle(Point('E'),Point('H'),Point('F')) - (((sympy.simplify('15') * Variable('x')) / sympy.simplify('180')) * sympy.simplify('pi'))), (Angle(Point('G'),Point('E'),Point('H')) - Variable('angle_2')), (Angle(Point('F'),Point('E'),Point('H')) - Variable('angle_1')), Between(Point('H'),Point('F'),Point('G')), Collinear(Point('F'),Point('G'),Point('H')), (Length(Point('E'),Point('F')) - Length(Point('F'),Point('G'))), (Length(Point('F'),Point('G')) - Length(Point('E'),Point('G'))), (Length(Point('E'),Point('G')) - Length(Point('E'),Point('F'))), (Angle(Point('F'),Point('E'),Point('H')) - Angle(Point('G'),Point('E'),Point('H'))), (Length(Point('E'),Point('F')) - Length(Point('F'),Point('G'))), (Length(Point('F'),Point('G')) - Length(Point('E'),Point('G'))), (Length(Point('E'),Point('G')) - Length(Point('E'),Point('F'))), (Angle(Point('F'),Point('E'),Point('H')) - Angle(Point('G'),Point('E'),Point('H')))]
goal = Variable('angle_2')
solution = '(30)/180*pi'

diagrammatic_relations = [SameSide(Point('F'),Point('H'),Point('E'),Point('G')), SameSide(Point('G'),Point('H'),Point('E'),Point('F')), OppositeSide(Point('F'),Point('G'),Point('E'),Point('H')), NotCollinear(Point('E'),Point('F'),Point('G')), NotCollinear(Point('E'),Point('F'),Point('H')), NotCollinear(Point('E'),Point('G'),Point('H'))]
