import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('I'),Point('W')) - Length(Point('N'),Point('W'))), (Length(Point('N'),Point('W')) - Length(Point('I'),Point('N'))), (Length(Point('I'),Point('N')) - Length(Point('I'),Point('W'))), (Length(Point('N'),Point('W')) - sympy.simplify('5')), (Length(Point('I'),Point('W')) - Length(Point('N'),Point('W'))), (Length(Point('N'),Point('W')) - Length(Point('I'),Point('N'))), (Length(Point('I'),Point('N')) - Length(Point('I'),Point('W'))), (Length(Point('N'),Point('W')) - sympy.simplify('5')), (Length(Point('I'),Point('W')) - Variable('radius_I')), (Length(Point('I'),Point('N')) - Variable('radius_I'))]
goal = Angle(Point('N'),Point('I'),Point('W'))
solution = '60/180*pi'

diagrammatic_relations = [NotCollinear(Point('I'),Point('N'),Point('W'))]

new_diagrammatic_relations = {NotCollinear(Point('I'),Point('N'),Point('W'))}

