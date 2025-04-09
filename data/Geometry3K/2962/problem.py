import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('S'),Point('T')) - sympy.simplify('15')), (Angle(Point('R'),Point('S'),Point('T')) - sympy.simplify('93/180*pi')), (Length(Point('R'),Point('S')) - Variable('radius_S')), (Length(Point('S'),Point('T')) - Variable('radius_S'))]
goal = ((Variable('radius_S') ** 2) *  Angle(Point('R'),Point('S'),Point('T')) / sympy.simplify('2')) 
solution = '182.6'

diagrammatic_relations = [NotCollinear(Point('R'),Point('S'),Point('T'))]

new_diagrammatic_relations = {NotCollinear(Point('R'),Point('S'),Point('T'))}

