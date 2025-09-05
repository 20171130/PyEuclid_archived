import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('P'),Point('T')) - sympy.Rational('13.5000000000000')), (Length(Point('U'),Point('Q')) - sympy.Rational('3')), (Length(Point('P'),Point('S')) - Variable('x')), (Length(Point('Q'),Point('W')) - sympy.Rational('9')), Between(Point('P'),Point('R'),Point('S')), Collinear(Point('P'),Point('R'),Point('S')), Between(Point('Q'),Point('U'),Point('V')), Collinear(Point('Q'),Point('U'),Point('V')), (Angle(Point('R'),Point('T'),Point('S')) - Angle(Point('U'),Point('W'),Point('V'))), (Angle(Point('R'),Point('S'),Point('T')) - Angle(Point('U'),Point('V'),Point('W'))), (Length(Point('Q'),Point('U')) - Length(Point('Q'),Point('V'))), (Length(Point('P'),Point('S')) - Length(Point('P'),Point('R')))]
goal = Variable('x')
solution = '4.5'

diagrammatic_relations = [
    SameSide(Point('P'), Point('S'), Point('R'), Point('T')),
    OppositeSide(Point('R'), Point('S'), Point('P'), Point('T')),
    SameSide(Point('P'), Point('R'), Point('S'), Point('T')),
    NotCollinear(Point('R'), Point('S'), Point('T')),
    NotCollinear(Point('P'), Point('R'), Point('T')),
    Between(Point('P'), Point('R'), Point('S')),
    NotCollinear(Point('P'), Point('S'), Point('T')),

    SameSide(Point('Q'), Point('V'), Point('U'), Point('W')),
    OppositeSide(Point('U'), Point('V'), Point('Q'), Point('W')),
    SameSide(Point('Q'), Point('U'), Point('V'), Point('W')),
    NotCollinear(Point('U'), Point('V'), Point('W')),
    NotCollinear(Point('Q'), Point('U'), Point('W')),
    Between(Point('Q'), Point('U'), Point('V')),
    NotCollinear(Point('Q'), Point('V'), Point('W'))
]
