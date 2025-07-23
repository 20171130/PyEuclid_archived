import sympy as sp

a, b = sp.symbols('a b')
expr1 = 2*a - 2*b
terms1 = expr1.as_ordered_terms()
# print(terms1, terms1[0], terms1[0].args)
print(expr1)
expr2 = b - a
terms2 = expr2.as_ordered_terms()
# print(terms2, terms2[0], terms2[0].args)
print(expr2)
expr3 = -b + a
terms3 = expr3.as_ordered_terms()
# print(terms3, terms3[0], terms3[0].args)
print(expr3)


for expr in [expr1, expr2, expr3]:
    terms = expr.as_ordered_terms()
    if isinstance(terms[0], sp.core.mul.Mul) and terms[0].args[0].is_constant():
        print('oo', expr)
        print('!!', terms[0].args[0])
        expr = expr/terms[0].args[0]
    print(expr)
# print(expr1, expr2)