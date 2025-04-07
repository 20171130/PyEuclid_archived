import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


relations = [(Length(Point('T'),Point('V')) - sympy.simplify('11')), (Length(Point('T'),Point('U')) - Variable('x')), (Length(Point('U'),Point('V')) - sympy.simplify('7')), Between(Point('B'),Point('T'),Point('V')), Collinear(Point('B'),Point('T'),Point('V')), (Length(Point('T'),Point('U')) - Variable('radius_T')), (Length(Point('B'),Point('T')) - Variable('radius_T')), (Angle(Point('T'),Point('U'),Point('V')) - sympy.simplify('pi/2'))]
goal = Variable('x')
solution = '8.5'

diagrammatic_relations = {SameSide(Point('B'),Point('T'),Point('U'),Point('V')), NotCollinear(Point('B'),Point('U'),Point('V')), NotCollinear(Point('B'),Point('T'),Point('U')), OppositeSide(Point('T'),Point('V'),Point('B'),Point('U')), SameSide(Point('B'),Point('V'),Point('T'),Point('U')), NotCollinear(Point('T'),Point('U'),Point('V'))}
