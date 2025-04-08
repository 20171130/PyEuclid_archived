import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('D'),Point('E')) - sympy.simplify('14')), (Length(Point('D'),Point('C')) - sympy.simplify('8')), (Length(Point('P'),Point('T')) - sympy.simplify('6')), (Length(Point('A'),Point('E')) - sympy.simplify('11')), Similar5P(Point('A'),Point('B'),Point('C'),Point('D'),Point('E'),Point('P'),Point('Q'),Point('R'),Point('S'),Point('T')),  Similar5P(Point('A'),Point('B'),Point('C'),Point('D'),Point('E'),Point('P'),Point('Q'),Point('R'),Point('S'),Point('T'))]
goal = Length(Point('R'),Point('S'))
solution = '48/(11)'

diagrammatic_relations = set()
