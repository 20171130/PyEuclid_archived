import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Angle(Point('E'),Point('H'),Point('G'))-sympy.simplify('pi/3')), (Length(Point('G'),Point('H')) - sympy.simplify('5')), (Length(Point('E'),Point('H')) - sympy.simplify('5')),(Length(Point('A'),Point('D')) - Length(Point('C'),Point('D'))), (Length(Point('C'),Point('D')) - Length(Point('C'),Point('E'))), (Length(Point('C'),Point('E')) - Length(Point('E'),Point('G'))), (Length(Point('E'),Point('G')) - Length(Point('F'),Point('G'))), (Length(Point('F'),Point('G')) - Length(Point('A'),Point('F'))), (Length(Point('A'),Point('F')) - Length(Point('A'),Point('D'))), (Angle(Point('A'),Point('D'),Point('C')) - Angle(Point('D'),Point('C'),Point('E'))), (Angle(Point('D'),Point('C'),Point('E')) - Angle(Point('C'),Point('E'),Point('G'))), (Angle(Point('C'),Point('E'),Point('G')) - Angle(Point('E'),Point('G'),Point('F'))), (Angle(Point('E'),Point('G'),Point('F')) - Angle(Point('A'),Point('F'),Point('G'))), (Angle(Point('A'),Point('F'),Point('G')) - Angle(Point('D'),Point('A'),Point('F'))), (Angle(Point('D'),Point('A'),Point('F')) - Angle(Point('A'),Point('D'),Point('C')))]
goal = Area(Point('E'),Point('H'),Point('G')) * 6
solution = '65.0'

diagrammatic_relations = [NotCollinear(Point('E'),Point('H'),Point('G'))]
