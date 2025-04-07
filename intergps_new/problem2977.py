import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


relations = [(Length(Point('D'),Point('H')) - ((sympy.simplify('2') * Variable('x')) + sympy.simplify('4'))), (Length(Point('G'),Point('H')) - sympy.simplify('7')), (Length(Point('H'),Point('J')) - sympy.simplify('10')), (Length(Point('D'),Point('G')) - ((sympy.simplify('2') * Variable('x')) - sympy.simplify('2'))), Between(Point('D'),Point('G'),Point('J')), Collinear(Point('D'),Point('G'),Point('J')), (Angle(Point('G'),Point('D'),Point('H')) - Angle(Point('G'),Point('H'),Point('J')))]
goal = Length(Point('D'),Point('G'))
solution = '14'

diagrammatic_relations = {NotCollinear(Point('G'),Point('H'),Point('J')), SameSide(Point('D'),Point('G'),Point('H'),Point('J')), NotCollinear(Point('D'),Point('H'),Point('J')), SameSide(Point('D'),Point('J'),Point('G'),Point('H')), OppositeSide(Point('G'),Point('J'),Point('D'),Point('H')), NotCollinear(Point('D'),Point('G'),Point('H')), Between(Point('D'),Point('G'),Point('J'))}
