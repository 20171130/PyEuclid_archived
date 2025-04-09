import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('B'),Point('C')) - Variable('a')), (Length(Point('A'),Point('C')) - Variable('b')), (Length(Point('A'),Point('B')) - Variable('c')), Perpendicular(Point('A'),Point('C'),Point('B'),Point('C')), (Variable('a') - sympy.simplify('14')), (Variable('b') - sympy.simplify('48')), (Variable('c') - sympy.simplify('50')), (Variable('a') - sympy.simplify('14')), (Variable('b') - sympy.simplify('48')), (Variable('c') - sympy.simplify('50'))]
goal = sympy.sin(Angle(Point('B'),Point('A'),Point('C')))
solution = '0.28'

diagrammatic_relations = [NotCollinear(Point('A'),Point('B'),Point('C'))]

new_diagrammatic_relations = {NotCollinear(Point('A'),Point('B'),Point('C'))}

