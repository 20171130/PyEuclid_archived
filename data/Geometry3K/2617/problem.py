import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('D'),Point('F')) - Variable('e')), (Length(Point('D'),Point('E')) - Variable('f')), (Length(Point('E'),Point('F')) - Variable('d')), (Angle(Point('D'),Point('E'),Point('F')) - sympy.simplify('108/180*pi')), (Angle(Point('D'),Point('F'),Point('E')) - sympy.simplify('26/180*pi')), (Variable('f') - sympy.simplify('20')), (Angle(Point('D'),Point('E'),Point('F')) - sympy.simplify('108/180*pi')), (Angle(Point('D'),Point('F'),Point('E')) - sympy.simplify('26/180*pi')), (Variable('f') - sympy.simplify('20'))]
goal = Variable('d')
solution = '33'

diagrammatic_relations = [NotCollinear(Point('D'),Point('E'),Point('F'))]

new_diagrammatic_relations = {NotCollinear(Point('D'),Point('E'),Point('F'))}

