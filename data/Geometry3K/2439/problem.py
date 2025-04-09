import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Angle(Point('S'),Point('R'),Point('T')) - sympy.simplify('70/180*pi')), (Length(Point('R'),Point('T')) - Length(Point('R'),Point('S')))]
goal = Angle(Point('R'),Point('S'),Point('T'))
solution = '(55)/180*pi'

diagrammatic_relations = [NotCollinear(Point('R'),Point('S'),Point('T'))]

new_diagrammatic_relations = {NotCollinear(Point('R'),Point('S'),Point('T'))}

