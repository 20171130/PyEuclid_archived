import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [Between(Point('J'),Point('A'),Point('B')), Collinear(Point('A'),Point('B'),Point('J')), Between(Point('B'),Point('A'),Point('C')), Collinear(Point('A'),Point('B'),Point('C')), Between(Point('B'),Point('A'),Point('K')), Collinear(Point('A'),Point('B'),Point('K')), Between(Point('B'),Point('A'),Point('D')), Collinear(Point('A'),Point('B'),Point('D')), Between(Point('B'),Point('C'),Point('J')), Collinear(Point('B'),Point('C'),Point('J')), Between(Point('B'),Point('J'),Point('K')), Collinear(Point('B'),Point('J'),Point('K')), Between(Point('B'),Point('D'),Point('J')), Collinear(Point('B'),Point('D'),Point('J')), Between(Point('C'),Point('A'),Point('K')), Collinear(Point('A'),Point('C'),Point('K')), Between(Point('C'),Point('A'),Point('D')), Collinear(Point('A'),Point('C'),Point('D')), Between(Point('C'),Point('J'),Point('K')), Collinear(Point('C'),Point('J'),Point('K')), Between(Point('C'),Point('D'),Point('J')), Collinear(Point('C'),Point('D'),Point('J')), Between(Point('C'),Point('B'),Point('K')), Collinear(Point('B'),Point('C'),Point('K')), Between(Point('C'),Point('B'),Point('D')), Collinear(Point('B'),Point('C'),Point('D')), Between(Point('K'),Point('A'),Point('D')), Collinear(Point('A'),Point('D'),Point('K')), Between(Point('K'),Point('D'),Point('J')), Collinear(Point('D'),Point('J'),Point('K')), Between(Point('K'),Point('B'),Point('D')), Collinear(Point('B'),Point('D'),Point('K')), Between(Point('K'),Point('C'),Point('D')), Collinear(Point('C'),Point('D'),Point('K')), (Length(Point('B'),Point('C')) - sympy.simplify('5.40000000000000')), (Length(Point('B'),Point('C')) - sympy.simplify('5.40000000000000')), (Length(Point('A'),Point('J')) - 10), (Length(Point('C'),Point('J')) - 10), (Length(Point('B'),Point('K')) - 8), (Length(Point('D'),Point('K')) - 8)]
goal = Length(Point('J'),Point('K'))
solution = '12.6'

diagrammatic_relations = [SameSide(Point('C'),Point('K'),Point('A'),Point('J'))]
