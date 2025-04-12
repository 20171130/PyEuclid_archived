import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Angle(Point('B'),Point('A'),Point('C')) - sympy.simplify('60/180*pi')), (Length(Point('B'),Point('C')) - sympy.simplify('12')), (Length(Point('A'),Point('C')) - sympy.simplify('11'))]
goal = Angle(Point('A'),Point('B'),Point('C')) * sympy.simplify('180/pi')
solution = '52.5'

diagrammatic_relations = [NotCollinear(Point('A'),Point('B'),Point('C'))]

new_diagrammatic_relations = {NotCollinear(Point('A'),Point('B'),Point('C'))}

