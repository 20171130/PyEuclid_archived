import sympy

from pyeuclid.formalization.relation import *

pi = sympy.pi


relations =[(Length(Point('D'),Point('F')) + Length(Point('G'),Point('B')) + Length(Point('A'),Point('H')) - 5),(Length(Point('B'),Point('G')) - sympy.simplify('2')), (Length(Point('C'),Point('D')) - sympy.simplify('5')), (Length(Point('A'),Point('B')) - sympy.simplify('2')), (Length(Point('E'),Point('H')) - sympy.simplify('5')), (Length(Point('C'),Point('E')) - sympy.simplify('5')), (Length(Point('F'),Point('G')) - sympy.simplify('2')), Between(Point('F'),Point('A'),Point('D')), Collinear(Point('A'),Point('D'),Point('F')), Between(Point('A'),Point('D'),Point('H')), Collinear(Point('A'),Point('D'),Point('H')), Between(Point('F'),Point('D'),Point('H')), Collinear(Point('D'),Point('F'),Point('H')), Between(Point('A'),Point('F'),Point('H')), Collinear(Point('A'),Point('F'),Point('H'))]
goal = Length(Point('D'),Point('C'))+Length(Point('C'),Point('E'))+Length(Point('E'),Point('H')) + Length(Point('H'),Point('A'))+Length(Point('A'),Point('B'))+Length(Point('B'),Point('G'))+Length(Point('F'),Point('G'))+Length(Point('F'),Point('D'))
solution = '24'

diagrammatic_relations = set()