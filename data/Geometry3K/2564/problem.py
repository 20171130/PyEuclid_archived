import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [Rectangle(Point('C'),Point('D'),Point('E'),Point('B')),Length(Point('D'),Point('E'))-5, Length(Point('E'),Point('B'))-10, Length(Point('A'),Point('J'))-5/2]
goal = Area(Point('C'),Point('D'),Point('E'),Point('B'))-(Length(Point('A'),Point('J')) ** 2) * sympy.simplify('pi') *2
solution = '10.7'

diagrammatic_relations = set()
new_diagrammatic_relations = set()