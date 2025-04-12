import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('N'),Point('P')) - (sympy.simplify('20') * sympy.sqrt(sympy.simplify('2')))), (Angle(Point('N'),Point('P'),Point('O')) - sympy.simplify('38/180*pi')), (Length(Point('N'),Point('O')) - Variable('x')), Perpendicular(Point('N'),Point('O'),Point('O'),Point('P'))]
goal = Variable('x')
solution = '17.4'

diagrammatic_relations = {NotCollinear(Point('N'),Point('O'),Point('P'))}
