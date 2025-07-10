import re
import sympy
import signal

from typing import List
from pathlib import Path

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
        return points[min_index:] + points[:min_index]


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


class Traced():
    def __init__(self, expr, depth=0, sources=[]):
        if isinstance(expr, Traced):
            sources = expr.sources
            depth = expr.depth
            expr = expr.expr
        terms = expr.as_ordered_terms()
        if isinstance(terms[0], sympy.core.mul.Mul) and terms[0].args[0].is_constant():
            expr = expr/terms[0].args[0]
        self.expr = expr
        self.symbol = None
        self.redundant = False
        self.trivial = False
        self.sources = sources
        self.str_rep = None
        self.negated_str_rep = None
        self.kinds = []
        self.rank = 0 # priority in the same depth
        self.depth = max([depth] + [getattr(item, "depth", 0) for item in self.sources])
        for key in ("free_symbols", "args"):
            setattr(self, key, getattr(self.expr, key))
    
    def subs(self, key, value):
        if isinstance(value, Traced):
            if len(self.sources) >0 and isinstance(self.sources[0], Traced):
                sources = [item for item in self.sources] + [value]
            else:
                sources = [self, value]
            value.symbol = key
            value = value.expr
        else:
            sources = self.sources
        expr = self.expr.subs(key, value)
        other = Traced(expr, sources=sources)
        other.symbol = self.symbol
        return other
    
    def __str__(self):
        if self.str_rep is None:
            if not self.symbol is None:
                self.str_rep = str(sympy.simplify(self.symbol - self.expr))
                self.negated_str_rep = str(sympy.simplify(-self.symbol + self.expr))
            else:
                self.str_rep = str(sympy.simplify(self.expr))
                self.negated_str_rep = str(sympy.simplify(-self.expr))
        return self.str_rep
    
    def __repr__(self):
        return str(self)
    
    def __eq__(self, other):
        return hash(self) == hash(other)
    
    def __hash__(self):
        return hash(self.expr)

        
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
    
from sympy.core import Add, Mul, Pow, Symbol

def is_linear(expr):
    for term in Add.make_args(expr):
        for factor in Mul.make_args(term):
            if isinstance(factor, Pow):
                base, exp = factor.args
                if exp != 1:
                    return False
            elif isinstance(factor, Symbol):
                pass
            elif factor.free_symbols:
                return False
    return True
    
    
def classify_equations(equations: List[Traced], var_types):
    angle_linear, length_linear, length_ratio, others = [], [], [], []
    for eqn in equations:
        if not eqn.kinds:
            kinds = []
            expr = eqn.expr
            assert isinstance(expr, sympy.core.add.Add)
            var_type = set()
            for symbol in expr.free_symbols:
                if "Angle" in str(symbol):
                    var_type.add("Angle")
                elif "Length" in str(symbol):
                    var_type.add("Length")
                else:
                    if symbol in var_types:
                        var_type.add(var_types[symbol])
            if not len(var_type) == 1:
                kinds = ["others"]
            else:
                if "Angle" in var_type:
                    if is_linear(expr):
                        kinds = ["angle_linear"]
                    else:
                        kinds = ["others"]
                else:
                    if is_linear(expr):
                        kinds.append("length_linear")
                    if len(expr.args) == 2:
                        lhs, rhs = expr.args
                        rhs = - rhs
                        expr = []
                        for factor in Mul.make_args(lhs/rhs):
                            if isinstance(factor, Pow):
                                expr.append(factor.args[0]*factor.args[1])
                            elif isinstance(factor, Symbol):
                                expr.append(factor)
                        if is_linear(Add(*expr)):
                            kinds.append("length_ratio")
                    if len(kinds) == 0:
                        kinds.append("others")
            eqn.kinds = kinds
        if "angle_linear" in eqn.kinds:
            angle_linear.append(eqn)
        if "length_linear" in eqn.kinds:
            length_linear.append(eqn)
        if "length_ratio" in eqn.kinds:
            length_ratio.append(eqn)
        if "others" in eqn.kinds:
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

eps = 1e-3
def is_small(x):
    if len(x.free_symbols) > 0:
        return False
    if hasattr(x, "evalf"):
        x = x.evalf()
    try:
        return abs(x) < eps
    except:
        assert False

def check_equalities(equalities):
    if not type(equalities) in (tuple, list):
        equalities = [equalities]
    for cond in equalities:
        if not (isinstance(cond, sympy.logic.boolalg.BooleanTrue) or isinstance(cond, sympy.core.numbers.Zero) or is_small(cond)):
            return False
    return True