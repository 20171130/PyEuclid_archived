import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


relations = [(Angle(Point('I'),Point('J'),Point('F'))-sympy.simplify('2*pi/8')), (Length(Point('F'),Point('J')) - 6), Length(Point('I'),Point('J'))-6]
goal = Area(Point('I'),Point('J'),Point('F')) * 8
solution = '101.8'

diagrammatic_relations = {NotCollinear(Point('I'),Point('J'),Point('F'))}