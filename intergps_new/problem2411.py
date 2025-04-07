import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


relations = [Between(Point('B'),Point('A'),Point('C')), Collinear(Point('B'),Point('A'),Point('C')), Length(Point('A'),Point('B'))- 5, Length(Point('C'),Point('B'))- 5]
goal = (Length(Point('A'),Point('C')) ** 2 - Length(Point('B'),Point('C'))**2 - Length(Point('B'),Point('C'))**2) * pi
solution = '157.1'

diagrammatic_relations = set()