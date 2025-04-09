import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('R'),Point('S')) - sympy.simplify('20.7000000000000')), (Length(Point('F'),Point('G')) - Variable('x')), (Length(Point('S'),Point('T')) - sympy.simplify('10')), (Length(Point('R'),Point('T')) - sympy.simplify('15')), (Length(Point('E'),Point('F')) - sympy.simplify('11.2500000000000')), (Angle(Point('S'),Point('R'),Point('T')) - sympy.simplify('27/180*pi')), (Angle(Point('R'),Point('T'),Point('S')) - sympy.simplify('110/180*pi')), (Angle(Point('E'),Point('F'),Point('G')) - sympy.simplify('110/180*pi')), (Angle(Point('F'),Point('E'),Point('G')) - sympy.simplify('27/180*pi')), (Angle(Point('R'),Point('S'),Point('T')) - sympy.simplify('43/180*pi')), Similar(Point('R'),Point('T'),Point('S'),Point('E'),Point('F'),Point('G'))]
goal = Length(Point('F'),Point('G'))
solution = '7.5'

diagrammatic_relations = [NotCollinear(Point('R'),Point('S'),Point('T'))]

new_diagrammatic_relations = {NotCollinear(Point('R'),Point('S'),Point('T'))}

