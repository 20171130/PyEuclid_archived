import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('A'),Point('B')) - sympy.simplify('12')), (Length(Point('C'),Point('D')) - sympy.simplify('8')), (Angle(Point('A'),Point('D'),Point('E')) - sympy.simplify('30/180*pi')), Between(Point('E'),Point('A'),Point('B')), Collinear(Point('A'),Point('B'),Point('E')), Perpendicular(Point('A'),Point('E'),Point('D'),Point('E')), (Length(Point('A'),Point('D')) - Length(Point('B'),Point('C'))), Trapezoid(Point('A'),Point('B'),Point('C'),Point('D'))]
goal = Area(Point('A'),Point('B'),Point('C'),Point('D'))
solution = '34.6'

diagrammatic_relations = set()

new_diagrammatic_relations = set()

