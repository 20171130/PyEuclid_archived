import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


relations = [Between(Point('D'),Point('C'),Point('B')), Collinear(Point('D'),Point('C'),Point('B')), Length(Point('C'),Point('D'))-Length(Point('D'),Point('B')),Length(Point('E'),Point('D'))-Length(Point('D'),Point('B')), Length(Point('E'),Point('C'))-5, Angle(Point('C'),Point('B'),Point('E'))-sympy.simplify('30*pi/180'), Angle(Point('C'),Point('E'),Point('B'))-sympy.simplify('pi/2')]
goal = Length(Point('C'),Point('D')) ** 2 * sympy.simplify('pi') - Area(Point('C'),Point('E'),Point('B'))
solution = '56.9'

diagrammatic_relations = {NotCollinear(Point('B'), Point('C'), Point('E')), NotCollinear(Point('B'), Point('D'), Point('E')), NotCollinear(Point('C'), Point('D'), Point('E'))}