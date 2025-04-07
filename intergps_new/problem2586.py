import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


relations = [(Angle(Point('L'),Point('M'),Point('P')) - sympy.simplify('60/180*pi')), (Angle(Point('L'),Point('P'),Point('M')) - sympy.simplify('60/180*pi')), (Length(Point('M'),Point('P')) - sympy.simplify('4')),  (Length(Point('L'),Point('P')) - ((sympy.simplify('5') * Variable('x')) - sympy.simplify('3')))]
goal = Variable('x')
solution = '1.4'

diagrammatic_relations = {NotCollinear(Point('L'),Point('M'),Point('P'))}
