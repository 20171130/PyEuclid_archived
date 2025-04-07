import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


relations = [(Length(Point('M'),Point('N')) - sympy.simplify('39')), (Length(Point('M'),Point('P')) - sympy.simplify('36')), (Length(Point('N'),Point('P')) - sympy.simplify('15')), Perpendicular(Point('M'),Point('P'),Point('N'),Point('P'))]
goal = sympy.sin(Angle(Point('M'),Point('N'),Point('P')))
solution = '0.92'

diagrammatic_relations = {NotCollinear(Point('M'),Point('N'),Point('P'))}
