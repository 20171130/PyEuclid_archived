import re
import sympy
from sympy import Add, Mul, Pow, Symbol, Rational, cancel
import signal

from typing import List
from pathlib import Path
from fractions import Fraction

ROOT_DIR = Path(__file__).parents[2]
MAX_DIAGRAM_ATTEMPTS = 1000


class TimeoutException(Exception):
    pass


class Timeout:
    def __init__(self, seconds):
        self.seconds = seconds

    def __enter__(self):
        signal.signal(signal.SIGALRM, self._handle_timeout)
        signal.setitimer(signal.ITIMER_REAL, self.seconds)

    def __exit__(self, exc_type, exc_val, exc_tb):
        signal.setitimer(signal.ITIMER_REAL, 0)  # Cancel timer
        signal.signal(signal.SIGALRM, signal.SIG_DFL)

    def _handle_timeout(self, signum, frame):
        raise TimeoutException("Operation timed out")


def sort_points(*points):
    return sorted(points, key=lambda i: i.name)

def sort_cyclic_points(*points):
    min_index = min(range(len(points)), key=lambda i: points[i].name)
    if str(points[(min_index+1) % len(points)]) > str(points[(min_index-1) % len(points)]):
        remaining_list = list(points[min_index:] + points[:min_index])[1:]
        return [points[min_index]] + remaining_list[::-1]
    else:
        return list(points[min_index:] + points[:min_index])


def ordered_groups(g1, g2):
    assert len(g1) == len(g2)
    for a, b in zip(g1, g2):
        if a.name != b.name:
            return a.name < b.name
    return True


def get_point_mapping(g1, g2):
    mapping = {}
    for p1, p2 in zip(g1, g2):
        mapping[p1] = p2
    return mapping


def sort_point_groups(g1, g2, mapping=False): 
    sorted_g1 = sort_points(*g1)
    sorted_g2 = sort_points(*g2)
    
    if not ordered_groups(sorted_g1, sorted_g2):
        g1, g2 = g2, g1
        sorted_g1, sorted_g2 = sorted_g2, sorted_g1
    
    if mapping:
        mapping = get_point_mapping(g1, g2)
        sorted_g2 = [mapping[p] for p in sorted_g1]
    
    return sorted_g1 + sorted_g2


def sort_cyclic_point_groups(g1, g2, mapping=False): 
    sorted_g1 = sort_cyclic_points(*g1)
    sorted_g2 = sort_cyclic_points(*g2)
    
    if not ordered_groups(sorted_g1, sorted_g2):
        g1, g2 = g2, g1
        sorted_g1, sorted_g2 = sorted_g2, sorted_g1
    
    if mapping:
        mapping = get_point_mapping(g1, g2)
        sorted_g2 = [mapping[p] for p in sorted_g1]

    return sorted_g1 + sorted_g2


class UnionFind:
    def __init__(self):
        self.parent = {}
        self.rank = {}

    def find(self, item):
        neg = getattr(item, "neg", False)
        if neg:
            item = -item
        if not item in self.parent:
            self.add(item)
            return -item if neg else item
        if self.parent[item] != item:
            self.parent[item] = self.find(self.parent[item])
        return -self.parent[item] if neg else self.parent[item]

    def union(self, item1, item2):
        if (type(item1).__name__ == 'Length' and type(item1).__name__ == 'Angle') or (type(item1).__name__ == 'Angle' and type(item1).__name__ == 'Length'):
            breakpoint()
            assert False
        root1 = self.find(item1)
        root2 = self.find(item2)
        neg = getattr(root1, "neg", False) ^ getattr(root2, "neg", False)
        if getattr(root1, "neg", False):
            root1 = - root1
        if getattr(root2, "neg", False):
            root2 = - root2
        if root1 != root2:
            if self.rank[root1] > self.rank[root2]:
                self.parent[root2] = -root1 if neg else root1
            elif self.rank[root1] < self.rank[root2]:
                self.parent[root1] = -root2 if neg else root2
            else:
                self.parent[root2] = -root1 if neg else root1
                self.rank[root1] += 1

    def add(self, item):
        if getattr(item, "neg", False):
            item = -item
        if item not in self.parent:
            self.parent[item] = item
            self.rank[item] = 0

    def equivalence_classes(self):
        dic = {}
        for item in self.parent:
            root = self.find(item)
            if root in dic:
                dic[root].append(item)
            else:
                dic[root] = [item]
        return dic

    def merge_eq(uf, v1, v2):
        uf.add(v1)
        uf.add(v2)
        uf.union(v1, v2)
        for v in [v1, v2]:
            if uf.parent[v] != v:
                v.rep_by = uf.parent[v]
                setattr(v.rep_by, "rep_by", None)


# class Traced():
#     def __init__(self, expr, depth=0, sources=[], redundant=False):
#         if isinstance(expr, Traced):
#             depth = expr.depth
#             sources = expr.sources
#             redundant = expr.redundant
#             expr = expr.expr
        
#         # num, den = sympy.together(expr).as_numer_denom()
#         # expr = num
#         terms = expr.as_ordered_terms()
#         if isinstance(terms[0], sympy.core.mul.Mul) and terms[0].args[0].is_constant():
#             expr = expr/terms[0].args[0]
#         self.expr = expr
#         self.redundant = redundant
#         self.sources = sources
#         self.kinds = []
#         self.depth = max([depth] + [getattr(item, "depth", 0) for item in self.sources])
#         for key in ("free_symbols", "args"):
#             setattr(self, key, getattr(self.expr, key))
    
#     def subs(self, key, value):
#         if isinstance(value, Traced):
#             if len(self.sources) > 0 and isinstance(self.sources[0], Traced):
#                 sources = [item for item in self.sources] + [value]
#             else:
#                 sources = [self, value]
#             value.symbol = key
#             value = value.expr
#         else:
#             sources = self.sources
#         expr = self.expr.subs(key, value)
#         other = Traced(expr, sources=sources)
#         return other
    
#     def __str__(self):
#         return str(self.expr)
    
#     def __repr__(self):
#         return str(self)
    
#     def __eq__(self, other):
#         return hash(self) == hash(other)
    
#     def __hash__(self):
#         return hash(self.expr)


class Traced:
    def __init__(self, expr, depth=0, sources=None, redundant=None, approx_sig=16):
        if isinstance(expr, Traced):
            depth = expr.depth
            sources = list(expr.sources) if expr.sources else []
            redundant = set(expr.redundant) if expr.redundant else set()
            expr = expr.expr

        sources = sources or []
        redundant = redundant or set()

        terms = expr.as_ordered_terms()
        if isinstance(terms[0], sympy.core.mul.Mul) and terms[0].args[0].is_constant():
            expr = expr/terms[0].args[0]

        # self._approx_sig = int(approx_sig) if approx_sig else 0
        # if self._approx_sig > 0:
        #     expr = self._approximate_numeric_factors(expr, self._approx_sig)

        self.expr = expr
        import math

        def round_sig(x, sig=3):
            if x == 0:
                return 0
            return round(x, sig - int(math.floor(math.log10(abs(x)))) - 1)
        if isinstance(expr, sympy.core.add.Add):
            args = []
            for arg in expr.args:
                if len(arg.free_symbols) == 0:
                    arg = round_sig(arg.evalf())
                args.append(arg)
            self.numerical_expr = sympy.core.add.Add(*args)
        else:
            self.numerical_expr = expr
        self.sources = list(sources)
        self.redundant = set(redundant)
        self.kinds = []
        
        source_depths = [getattr(s, "depth", 0) for s in self.sources]
        self.depth = max([depth] + source_depths) if self.sources else depth

        self.free_symbols = getattr(self.expr, "free_symbols", set())
        self.args = getattr(self.expr, "args", ())
        self.symbol = None

    @staticmethod
    def _is_numeric(expr):
        return isinstance(expr, sympy.Basic) and not expr.free_symbols

    @staticmethod
    def _is_simple_numeric(expr):
        return (expr.is_Integer or expr.is_Rational or 
                isinstance(expr, (sympy.Integer, sympy.Rational)) or
                expr.count_ops(visual=False) <= 2)

    @classmethod
    def _approximate_numeric_factors(cls, expr, sig_digits):
        if not isinstance(expr, sympy.Basic) or expr.is_Atom:
            return expr

        if expr.is_Add:
            new_args = [cls._approximate_numeric_factors(arg, sig_digits) for arg in expr.args]
            return sympy.Add(*new_args, evaluate=True)

        if expr.is_Mul:
            numeric_factors = []
            symbolic_factors = []
            
            for arg in expr.args:
                if cls._is_numeric(arg):
                    numeric_factors.append(arg)
                else:
                    symbolic_factors.append(cls._approximate_numeric_factors(arg, sig_digits))

            if symbolic_factors and numeric_factors:
                approximated_numerics = []
                for factor in numeric_factors:
                    if cls._is_simple_numeric(factor):
                        approximated_numerics.append(factor)
                    else:
                        approximated_numerics.append(sympy.Float(factor.evalf(sig_digits), sig_digits))
                return sympy.Mul(*(symbolic_factors + approximated_numerics), evaluate=True)
            else:
                new_args = [cls._approximate_numeric_factors(arg, sig_digits) for arg in expr.args]
                return sympy.Mul(*new_args, evaluate=True)

        if expr.is_Pow:
            base = cls._approximate_numeric_factors(expr.base, sig_digits)
            exp = expr.exp
            
            if cls._is_numeric(exp) and not cls._is_simple_numeric(exp):
                exp = sympy.Float(exp.evalf(sig_digits), sig_digits)
            else:
                exp = cls._approximate_numeric_factors(exp, sig_digits)
            
            return sympy.Pow(base, exp, evaluate=True)

        new_args = [cls._approximate_numeric_factors(arg, sig_digits) for arg in expr.args]
        return expr.func(*new_args, evaluate=True)

    def subs(self, key, value):
        if isinstance(value, Traced):
            sources = list(self.sources) + [value] if self.sources else [self, value]
            value.symbol = key
            value_expr = value.expr
        else:
            sources = list(self.sources)
            value_expr = value
        
        new_expr = self.expr.subs(key, value_expr)
        
        try:
            expanded = new_expr.expand()
            coeffs = expanded.as_coefficients_dict()
            if all(abs(float(c.evalf())) < 1e-8 for c in coeffs.values()):
                new_expr = sympy.Integer(0)
        except:
            pass
        
        return Traced(new_expr, depth=self.depth, sources=sources,
                    redundant=set(self.redundant), approx_sig=self._approx_sig)

    def __str__(self):
        return str(self.expr)

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return hash(self) == hash(other)
    
    def __hash__(self):
        return hash(self.numerical_expr)

# def _rationalize_floats(expr: sympy.Expr, *, tol: float = 1e-12, max_den: int = 10**6) -> sympy.Expr:
#     repl = {}
#     for f in expr.atoms(sympy.Float):
#         val = float(f)
#         frac = Fraction(val).limit_denominator(max_den)
#         r = sympy.Rational(frac.numerator, frac.denominator)
#         if abs(float(r) - val) <= tol * max(1.0, abs(val)):
#             repl[f] = r
#     return expr.xreplace(repl)


# def canon_key(expr):
#     # numerator in common-denominator form (cheap)
#     num, _ = sympy.together(expr).as_numer_denom()
#     if num.is_zero:
#         return ('ZERO',)

#     # fast float→rational snap (no nsimplify)
#     if num.has(sympy.Float):
#         repl = {}
#         for f in num.atoms(sympy.Float):
#             val = float(f)
#             frac = Fraction(val).limit_denominator(10**6)
#             r = sympy.Rational(frac.numerator, frac.denominator)
#             if abs(float(r) - val) <= 1e-12 * max(1.0, abs(val)):
#                 repl[f] = r
#         if repl:
#             num = num.xreplace(repl)

#     syms = tuple(sorted(num.free_symbols, key=str))

#     # polynomial path over QQ only (fast)
#     if syms and num.is_polynomial(*syms) and all(n.is_Rational for n in num.atoms(sympy.Number)):
#         try:
#             P = sympy.Poly(num, *syms, domain='QQ')
#             _, Pp = P.primitive()
#             if Pp.LC() < 0:
#                 Pp = -Pp
#             return ('POLY_QQ', syms, tuple(sorted(Pp.terms())))
#         except:
#             pass

#     # lightweight structural fallback (no global expand)
#     num = sympy.signsimp(sympy.powsimp(sympy.gcd_terms(num, clear=True), force=True))
#     ts = num.as_ordered_terms()
#     if ts:
#         c, _ = ts[0].as_coeff_Mul()
#         if c.is_negative:
#             num = -num
#     return ('NON_POLY', sympy.srepr(num))


# class Traced():
#     def __init__(self, expr, depth=0, sources=None, redundant=None):
#         if isinstance(expr, Traced):
#             depth     = expr.depth
#             sources   = list(expr.sources) if expr.sources else []
#             redundant = set(expr.redundant) if expr.redundant else set()
#             expr      = expr.expr

#         if sources is None:
#             sources = []
#         if redundant is None:
#             redundant = set()

#         terms = expr.as_ordered_terms()
#         if isinstance(terms[0], sympy.core.mul.Mul) and terms[0].args[0].is_constant():
#             expr = expr/terms[0].args[0]
#         self.expr = expr
#         self.sources = list(sources)
#         self.redundant = set(redundant)
#         self.kinds = []
#         self.depth = max([depth] + [getattr(item, "depth", 0) for item in self.sources])
#         for key in ("free_symbols", "args"):
#             setattr(self, key, getattr(self.expr, key))
#         self._key = canon_key(self.expr)
    
#     def subs(self, key, value):
#         if isinstance(value, Traced):
#             if self.sources and isinstance(self.sources[0], Traced):
#                 sources = list(self.sources) + [value]
#             else:
#                 sources = [self, value]
#             value.symbol = key
#             value_expr = value.expr
#         else:
#             sources = list(self.sources)
#             value_expr = value

#         new_expr = self.expr.subs(key, value_expr)
#         return Traced(new_expr, depth=self.depth, sources=sources, redundant=set(self.redundant))
    
#     def __str__(self):
#         return str(self.expr)
    
#     def __repr__(self):
#         return str(self)
    
#     def __hash__(self):
#         return hash(self._key)
    
#     def __eq__(self, other):
#         return isinstance(other, Traced) and self._key == other._key

        
def infer_eq_types(eq, var_types):
    eq_types = set()
    for symbol in eq.free_symbols:
        if "Length" in str(symbol):
            eq_types.add("Length")
        elif "Angle" in str(symbol):
            eq_types.add("Angle")
        elif symbol in var_types and not var_types[symbol] is None:
            eq_types.add(var_types[symbol])
    return eq_types


def is_linear(expr):
    for term in Add.make_args(expr):
        cnt = 0
        for factor in Mul.make_args(term):
            if factor.free_symbols:
                if isinstance(factor, Pow):
                    base, exp = factor.args
                    if exp != 1:
                        return False
                    cnt += 1
                elif isinstance(factor, Symbol):
                    cnt += 1
                else:
                    return False
        if cnt > 1:
            return False
    return True


def ratio_is_linear(expr):
    """
    True iff expr is const1*a/b - const2 OR const2 - const1*a/b,
    where const1,const2 are constant (no free symbols) and a,b are single Symbols.
    Robust for pi, E, sqrt(2), rationals, and either term order.
    """
    # Get the top-level terms (before putting over common denominator)
    terms = list(Add.make_args(expr))
    
    if len(terms) != 2:
        return False
    
    # We need exactly one ratio term and one constant term
    ratio_term = None
    const_term = None
    
    for term in terms:
        # Check if this term is a constant
        if term.free_symbols == set():
            if const_term is not None:
                return False  # Multiple constant terms
            const_term = term
            continue
            
        # Check if this term is of the form const * a / b
        # First, get numerator and denominator
        num, den = term.as_numer_denom()
        
        # Check if it's a ratio form at all
        if den == 1:
            continue  # Not a ratio
            
        # For the numerator: extract all factors that are constants vs symbols
        if isinstance(num, Symbol):
            num_symbols = [num]
            num_constants = []
        elif isinstance(num, Mul):
            factors = num.as_ordered_factors()
            num_symbols = [f for f in factors if isinstance(f, Symbol)]
            num_constants = [f for f in factors if f.free_symbols == set()]
            # Check for any remaining factors that are neither symbols nor constants
            remaining = [f for f in factors if f not in num_symbols and f not in num_constants]
            if remaining:
                continue  # Has complex factors
        else:
            # Could be a power, function, etc.
            if num.free_symbols == set():
                num_symbols = []
                num_constants = [num]
            elif len(num.free_symbols) == 1 and isinstance(list(num.free_symbols)[0], Symbol):
                # It's some function of a single symbol - not what we want
                continue
            else:
                continue
                
        # For the denominator: similar analysis
        if isinstance(den, Symbol):
            den_symbols = [den]
            den_constants = []
        elif isinstance(den, Mul):
            factors = den.as_ordered_factors()
            den_symbols = [f for f in factors if isinstance(f, Symbol)]
            den_constants = [f for f in factors if f.free_symbols == set()]
            # Check for any remaining factors that are neither symbols nor constants
            remaining = [f for f in factors if f not in den_symbols and f not in den_constants]
            if remaining:
                continue  # Has complex factors
        else:
            # Could be a power, function, etc.
            if den.free_symbols == set():
                den_symbols = []
                den_constants = [den]
            elif len(den.free_symbols) == 1 and isinstance(list(den.free_symbols)[0], Symbol):
                # It's some function of a single symbol - not what we want
                continue
            else:
                continue
        
        # We want exactly one symbol in numerator and one in denominator
        if len(num_symbols) != 1 or len(den_symbols) != 1:
            continue
            
        # Make sure the symbols are different
        if num_symbols[0] == den_symbols[0]:
            continue
            
        if ratio_term is not None:
            return False  # Multiple ratio terms
        ratio_term = term
    
    # We need exactly one ratio term and one constant term
    return ratio_term is not None and const_term is not None
    
def classify_equations(equations: List, var_types, cache=True):
    def _is_monomial_ratio(q: sympy.Expr) -> bool:
        q = cancel(q)
        if q.has(Add):
            return False
        for f in Mul.make_args(q):
            if f.is_Number:
                continue
            if isinstance(f, Symbol):
                continue
            if isinstance(f, Pow) and isinstance(f.base, Symbol) and (f.exp.is_Rational or f.exp.is_Integer):
                continue
            return False
        return True

    angle_linear, length_linear, length_ratio, others = [], [], [], []
    for eqn in equations:
        if not getattr(eqn, "kinds", None):
            kinds = set()
            expr = eqn.expr.expand()
            var_type = set()
            for symbol in expr.free_symbols:
                s = str(symbol)
                if "Angle" in s:
                    var_type.add("Angle")
                elif "Length" in s or "Area" in s:
                    var_type.add("Length")
                else:
                    if symbol in var_types:
                        var_type.add(var_types[symbol])

            if not isinstance(expr, (sympy.Add, sympy.Symbol)) or not len(var_type) == 1:
                kinds.add("others")
            else:
                if "Angle" in var_type:
                    if is_linear(expr):
                        kinds.add("angle_linear")
                    else:
                        kinds.add("others")
                else:
                    if is_linear(expr):
                        kinds.add("length_linear")
                        if len(expr.free_symbols) == 1:
                            kinds.add("length_ratio")
                    if len(expr.args) == 2:
                        lhs, rhs = expr.args
                        q = lhs / (-rhs)
                        if _is_monomial_ratio(q):
                            q = cancel(q)
                            tmp_terms = []
                            for f in Mul.make_args(q):
                                if isinstance(f, Symbol):
                                    tmp_terms.append(f)
                                elif isinstance(f, Pow) and isinstance(f.base, Symbol) and (f.exp.is_Rational or f.exp.is_Integer):
                                    tmp_terms.append(f.base * f.exp)
                            if tmp_terms and is_linear(Add(*tmp_terms)):
                                kinds.add("length_ratio")
                    if len(kinds) == 0:
                        kinds.add("others")
            if cache:
                eqn.kinds = kinds
        else:
            kinds = eqn.kinds

        if "angle_linear" in kinds:
            angle_linear.append(eqn)
        if "length_linear" in kinds:
            length_linear.append(eqn)
        if "length_ratio" in kinds:
            length_ratio.append(eqn)
        if "others" in kinds:
            others.append(eqn)

    return angle_linear, length_linear, length_ratio, others

def is_float(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def parse_expression(expr):
    symbols = {'Angle': [], 'Length': []}
    symbol_names = {'Angle': [], 'Length': []}
    
    for arg in expr.free_symbols:
        if arg.is_Symbol:
            match1 = re.match(r'Angle_(\w+)_(\w+)_(\w+)', arg.name)
            match2 = re.match(r'Length_(\w+)_(\w+)', arg.name)
        if match1:
            symbols['Angle'].append(arg)
            symbol_names['Angle'].append(list(match1.groups()))
        if match2:
            symbols['Length'].append(arg)
            symbol_names['Length'].append(list(match2.groups()))            
            
    return symbols, symbol_names

eps = 1e-8
def is_small(x):
    if len(x.free_symbols) > 0:
        return False
    if hasattr(x, "evalf"):
        x = x.evalf()
    try:
        return abs(x) < eps
    except:
        breakpoint()
        assert False

def check_equalities(equalities):
    if not type(equalities) in (tuple, list):
        equalities = [equalities]
    for cond in equalities:
        if not (isinstance(cond, sympy.logic.boolalg.BooleanTrue) or isinstance(cond, sympy.core.numbers.Zero) or is_small(cond)):
            return False
    return True