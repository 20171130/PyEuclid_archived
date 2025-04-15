import sympy
from pyeuclid.formalization.relation import *

pi = sympy.pi


conditions = [(Length(Point('F'),Point('N')) - (((sympy.simplify('1') / sympy.simplify('4')) * Variable('x')) + sympy.simplify('6'))), (Length(Point('I'),Point('P')) - (sympy.simplify('12') - (sympy.simplify('3') * Variable('y')))), (Length(Point('D'),Point('P')) - (sympy.simplify('16') - (sympy.simplify('5') * Variable('y')))), (Length(Point('A'),Point('N')) - ((sympy.simplify('2') * Variable('x')) - sympy.simplify('29'))),  (Length(Point('I'),Point('P')) - Length(Point('D'),Point('P')))]
goal = Variable('y')
solution = '2'

diagrammatic_relations = set()
new_diagrammatic_relations = set()