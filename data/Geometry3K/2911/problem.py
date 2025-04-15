import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Angle(Point('A'),Point('B'),Point('C')) - sympy.simplify('60/180*pi')), (Length(Point('B'),Point('C')) - Variable('a')), (Length(Point('A'),Point('C')) - Variable('b')), (Angle(Point('B'),Point('A'),Point('C')) - sympy.simplify('30/180*pi')), (Length(Point('A'),Point('B')) - Variable('c')), Perpendicular(Point('A'),Point('C'),Point('B'),Point('C')), (Variable('c') - sympy.simplify('5')), (Variable('c') - sympy.simplify('5'))]
goal = Variable('b')
solution = '2.5*sqrt(3)'

diagrammatic_relations = [NotCollinear(Point('A'),Point('B'),Point('C'))]

new_diagrammatic_relations = {NotCollinear(Point('A'),Point('B'),Point('C'))}

