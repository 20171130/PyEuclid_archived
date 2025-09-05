import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('A'),Point('B')) - sympy.simplify('12')), (Length(Point('C'),Point('D')) - sympy.simplify('8')), (Angle(Point('A'),Point('D'),Point('E')) - sympy.simplify('30/180*pi')), Between(Point('E'),Point('A'),Point('B')), Collinear(Point('A'),Point('B'),Point('E')), Perpendicular(Point('A'),Point('E'),Point('D'),Point('E')), (Length(Point('A'),Point('D')) - Length(Point('B'),Point('C'))), Trapezoid(Point('A'),Point('B'),Point('C'),Point('D')), Parallel(Point('A'),Point('B'),Point('C'),Point('D'))]
goal = Area(Point('A'),Point('B'),Point('C'),Point('D'))
solution = '34.6'



diagrammatic_relations = [
    SameSide(Point('B'), Point('E'), Point('C'), Point('D')),
    SameSide(Point('C'), Point('D'), Point('A'), Point('E')),
    OppositeSide(Point('B'), Point('D'), Point('A'), Point('C')),
    NotCollinear(Point('B'), Point('C'), Point('D')),
    NotCollinear(Point('A'), Point('B'), Point('D')),
    SameSide(Point('C'), Point('D'), Point('A'), Point('B')),
    SameSide(Point('D'), Point('E'), Point('B'), Point('C')),
    NotCollinear(Point('C'), Point('D'), Point('E')),
    SameSide(Point('A'), Point('E'), Point('B'), Point('D')),
    SameSide(Point('A'), Point('B'), Point('C'), Point('D')),
    SameSide(Point('A'), Point('E'), Point('B'), Point('C')),
    OppositeSide(Point('A'), Point('B'), Point('C'), Point('E')),
    SameSide(Point('C'), Point('E'), Point('A'), Point('D')),
    SameSide(Point('A'), Point('E'), Point('C'), Point('D')),
    SameSide(Point('C'), Point('D'), Point('B'), Point('E')),
    SameSide(Point('A'), Point('D'), Point('C'), Point('E')),
    SameSide(Point('B'), Point('E'), Point('A'), Point('D')),
    SameSide(Point('B'), Point('C'), Point('D'), Point('E')),
    NotCollinear(Point('B'), Point('C'), Point('E')),
    NotCollinear(Point('A'), Point('C'), Point('D')),
    OppositeSide(Point('A'), Point('B'), Point('D'), Point('E')),
    OppositeSide(Point('B'), Point('D'), Point('C'), Point('E')),
    SameSide(Point('A'), Point('D'), Point('B'), Point('C')),
    NotCollinear(Point('B'), Point('D'), Point('E')),
    OppositeSide(Point('D'), Point('E'), Point('A'), Point('C')),
    NotCollinear(Point('A'), Point('C'), Point('E')),
    Between(Point('E'), Point('A'), Point('B')),
    SameSide(Point('B'), Point('E'), Point('A'), Point('C')),
    OppositeSide(Point('A'), Point('C'), Point('D'), Point('E')),
    NotCollinear(Point('A'), Point('B'), Point('C')),
    OppositeSide(Point('C'), Point('E'), Point('B'), Point('D')),
    SameSide(Point('B'), Point('C'), Point('A'), Point('D')),
    OppositeSide(Point('A'), Point('C'), Point('B'), Point('D')),
    NotCollinear(Point('A'), Point('D'), Point('E')),
    Acute(Point('D'), Point('A'), Point('B')),
    Acute(Point('C'), Point('B'), Point('A')),
]

