import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


relations = [(Length(Point('B'),Point('X')) - sympy.simplify('13')), (Length(Point('A'),Point('X')) - sympy.simplify('5')), (Angle(Point('B'),Point('A'),Point('X')) - sympy.simplify('90/180*pi'))]
goal = sympy.tan(Angle(Point('A'),Point('X'),Point('B')))
solution = '(12)/(5)'

diagrammatic_relations = {NotCollinear(Point('A'),Point('B'),Point('X'))}
