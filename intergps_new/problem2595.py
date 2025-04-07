import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


relations = [Between(Point('D'),Point('B'),Point('C')), Collinear(Point('B'),Point('C'),Point('D')), Between(Point('S'),Point('B'),Point('C')), Collinear(Point('B'),Point('C'),Point('S')), Between(Point('D'),Point('C'),Point('S')), Collinear(Point('C'),Point('D'),Point('S')), Between(Point('S'),Point('B'),Point('D')), Collinear(Point('B'),Point('D'),Point('S')), Between(Point('C'),Point('B'),Point('R')), Collinear(Point('B'),Point('C'),Point('R')), Between(Point('D'),Point('B'),Point('R')), Collinear(Point('B'),Point('D'),Point('R')), Between(Point('S'),Point('B'),Point('R')), Collinear(Point('B'),Point('R'),Point('S')), Between(Point('C'),Point('D'),Point('R')), Collinear(Point('C'),Point('D'),Point('R')), Between(Point('C'),Point('R'),Point('S')), Collinear(Point('C'),Point('R'),Point('S')), Between(Point('D'),Point('R'),Point('S')), Collinear(Point('D'),Point('R'),Point('S')), (Length(Point('D'),Point('S')) - sympy.simplify('9')), (Length(Point('D'),Point('S')) - sympy.simplify('9')), (Length(Point('D'),Point('R')) - (sympy.simplify('20') / 2)), (Length(Point('B'),Point('S')) - (sympy.simplify('30') / 2)), (Length(Point('C'),Point('S')) - (sympy.simplify('30') / 2))]
goal = Length(Point('C'),Point('R'))
solution = '4'

diagrammatic_relations = set()
