import re
import sympy
import math
import numpy as np
import gurobipy as gp

from typing import List
from pathlib import Path
from stopit import ThreadingTimeout as Timeout
from sympy import factor_list
from gurobipy import GRB

ROOT_DIR = Path(__file__).parents[2]
MAX_DIAGRAM_ATTEMPTS = 100


def sort_points(*points):
    return sorted(points, key=lambda i: i.name)

def sort_cyclic_points(*points):
    min_index = min(range(len(points)), key=lambda i: points[i].name)
    if str(points[(min_index+1) % len(points)]) > str(points[(min_index-1) % len(points)]):
        remaining_list = list(points[min_index:] + points[:min_index])[1:]
        return [points[min_index]] + remaining_list[::-1]
    else:
        return points[min_index:] + points[:min_index]


def compare_names(g1, g2):
    assert len(g1) == len(g2)
    for a, b in zip(g1, g2):
        if a.name != b.name:
            return a.name < b.name
    return True


def get_point_mapping(g1, g2):
    mapping = {}
    for p1, p2 in zip(g1, g2):
        mapping[p1] = p2
        mapping[p2] = p1
    return mapping


def sort_point_groups(g1, g2, mapping=None):
    if not compare_names(g1, g2):
        g1, g2 = g2, g1
    
    if mapping:
        g2 = [mapping[p] for p in g1]
    
    return g1 + g2


def sqrt(x):
    return sympy.simplify(f"sqrt({x})")


def cos(x):
    return sympy.simplify(f"cos({x})")


def sin(x):
    return sympy.simplify(f"sin({x})")


def tan(x):
    return sympy.simplify(f"tan({x})")
    

def expand_definition(relation):
    if not type(relation) in (tuple, list):
        relation = relation,
    lst = []
    for prop in relation:
        if hasattr(prop, "definition"):
            for item in prop.definition():
                lst += expand_definition(item)
        else:
            lst += prop,
    return lst


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
        self.expr = expr
        self.symbol = None
        self.redundant = False
        self.sources = sources
        self.depth = max([depth] + [getattr(item, "depth", 0) for item in self.sources])
        for key in ("free_symbols", "args"):
            setattr(self, key, getattr(self.expr, key))
    
    def subs(self, key, value):
        assert isinstance(value, Traced)
        if len(self.sources)>0 and isinstance(self.sources[0], Traced):
            sources = [item for item in self.sources] + [value]
        else:
            sources = [self, value]
        value.symbol = key
        expr = self.expr.subs(key, value.expr)
        other = Traced(expr, sources=sources)
        other.symbol = self.symbol
        return other
    
    def __str__(self):
        if not self.symbol is None:
            return str(self.symbol - self.expr)
        return str(self.expr)
    def __repr__(self):
        return str(self)
    def __eq__(self, other):
        return hash(self) == hash(other)
    def __hash__(self):
        rep = f"{self}@{self.depth}"
        rep += " ".join([str(hash(item)) for item in self.sources])
        return hash(rep)


def classify_equations(equations: List[Traced]):
    angle_linear, length_linear, length_ratio, others = [], [], [], []
    cnst = r"(\d+|\d+\.\d*|pi)"
    cnst = f"{cnst}(\*{cnst})*(/{cnst})*"
    length = r"(length\w+\d*|variable\w+\d*)"
    angle = r"(angle\w+\d*|variable\w+\d*)"
    length_mono = f"({cnst}\*)?{length}(/{cnst})?"
    angle_mono = f"({cnst}\*)?{angle}(/{cnst})?"
    length_mono = f"({length_mono}|{cnst})"
    angle_mono = f"({angle_mono}|{cnst})"
    length_ratio_pattern = re.compile(
        f"^-?{length_mono}([\*/]{length_mono})* [+-] {length_mono}([\*/]{length_mono})*$")
    length_linear_pattern = re.compile(
        f"^-?{length_mono}( [+-] {length_mono})+$")
    angle_linear_pattern = re.compile(
        f"^-?{angle_mono}( [+-] {angle_mono})+$")
    for i, eq in enumerate(equations):
        tmp = str(eq).lower()
        if angle_linear_pattern.match(tmp):
            # eqangle, angle eq const, angle sum
            angle_linear.append(eq)
        elif length_ratio_pattern.match(tmp):
            # eqratio, length eq const, eqlength, linear equations involving length and variables
            length_ratio.append(eq)
        elif length_linear_pattern.match(tmp):
            length_linear.append(eq)
        else:
            others.append(eq)
    return angle_linear, length_linear, length_ratio, others
    
def is_float(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def parse_angle_expression(expr):
    angles = []
    angle_names = []
    for arg in expr.free_symbols:
        if arg.is_Symbol:
            match = re.match(r'Angle_(\w+)_(\w+)_(\w+)', arg.name)
            if match:
                angles.append(arg)
                angle_names.append(list(match.groups()))
    return angles, angle_names


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

def is_small(x):
    if len(x.free_symbols) > 0:
        return False
    if hasattr(x, "evalf"):
        x = x.evalf()
    try:
        return abs(x) < eps
    except:
        breakpoint()

eps = 1e-3
def process_solutions(var, eqn, solutions, var_types):
    symbols = eqn.free_symbols
    solutions = [item for item in solutions if len(item.free_symbols) == len(
        symbols) - 1]  # remove degenerate solutions
    if len(symbols) == 1:
        solutions = [sympy.re(sol.simplify())
                     for sol in solutions if abs(sympy.im(sol)) < 1e-3]
        if str(var).startswith("Angle"):
            solutions = {j for j in solutions if j >= 0 and j <= math.pi+eps}
            # Prioitize non-zero and non-flat angle
            if len(solutions) > 1:
                solutions = {j for j in solutions if j != 0 and j != sympy.pi}
        elif var_types.get(var, None) == "Angle":
            solutions = {j for j in solutions if j >=
                         0 and j <= 180+eps/math.pi*180}
            # Prioitize non-zero and non-flat angle
            if len(solutions) > 1:
                solutions = {j for j in solutions if j != 0 and j != 180}
        if len(solutions) > 1:
            solutions = [item for item in solutions if item >= 0]
        if len(solutions) > 1:
            solutions = [item for item in solutions if item > 0]
    if len(solutions) == 1:
        return solutions.pop()
    return None

def process_equation(eqn, check=False):
    if isinstance(eqn, sympy.core.add.Add):
        add_args = []
        for item in eqn.args:
            if isinstance(item, sympy.core.mul.Mul) and is_small(item.args[0]):
                continue
            add_args.append(item)
        eqn = sympy.core.add.Add(*add_args)
    if is_small(eqn):
        return sympy.sympify(0)
    eqn, denominator = eqn.as_numer_denom()
    try:
        with Timeout(0.1) as tt:
            factors = factor_list(eqn)
        if is_small(factors[0]):
            return sympy.sympify(0)
        factors = factors[1]  # removes constant coefficient
        factors = [item[0] for item in factors if not item[0].is_positive]
        if len(factors) == 0:
            if check:
                breakpoint()  # contradiction
                assert False
            else:
                return sympy.sympify(0)
        eqn = factors[0]
        for item in factors[1:]:
            eqn = eqn*item
    except:
        return eqn
    return eqn



def check_equalities(equalities):
    if not type(equalities) in (tuple, list):
        equalities = [equalities]
    for cond in equalities:
        if not (isinstance(cond, sympy.logic.boolalg.BooleanTrue) or isinstance(cond, sympy.core.numbers.Zero)):
            return False
    return True

        
def elim(equations, var_types):
    free_vars = []
    raw_equations = equations
    equations = [item.expr for item in equations]
    for eqn in equations:
        free_vars += eqn.free_symbols
    free_vars = set(free_vars)
    free_vars = list(free_vars)
    free_vars.sort(key=lambda x: x.name)
    exprs = {}
    # Triangulate
    for i, eqn in enumerate(equations):
        try:
            eqn = process_equation(eqn, check=True)
        except:
            breakpoint()
        if eqn == 0:
            raw_equations[i].redundant = True
            continue
        symbols = list(eqn.free_symbols)
        symbols.sort(key=lambda x: str(x))
        expr = None
        for var in symbols:
            solutions = None
            expr = None
            try:
                solutions = sympy.solve(eqn, var)
                expr = process_solutions(var, eqn, solutions, var_types)
            except:
                breakpoint()
                assert False
            if expr is None:
                continue
            else:
                break
        if expr is None:
            continue
        if expr == 0 and "length" in str(var).lower():
            breakpoint()
            assert False
        if expr == 0 and "radius" in str(var).lower():
            breakpoint()
            assert False
        if not var in exprs:
            exprs[var] = expr
        elif check_equalities(expr-exprs[var]):  # redundant equation
            equations[i] = sympy.sympify(0)
            raw_equations[i].redundant = True
            continue
        else:
            breakpoint()  # contradiction
            assert False
        if var in free_vars:
            free_vars.remove(var)
        eqns = [(idx+i+1, item) for idx,
                item in enumerate(equations[i+1:]) if var in item.free_symbols]
        for idx, item in eqns:
            if var in getattr(equations[idx], "free_symbols", []):
                equations[idx] = item.subs(var, exprs[var])

    # Diagonalize
    for i, (key, value) in enumerate(exprs.items()):
        for j, key1 in enumerate(exprs.keys()):
            if j == i:
                break
            if key in getattr(exprs[key1], "free_symbols", []):
                old = exprs[key1]
                exprs[key1] = exprs[key1].subs(key, value)
                if str(exprs[key1]) == "0" and "Length" in str(key1):
                    breakpoint()
                    assert False
                    pass
    exprs = {key: value for key, value in exprs.items()}
    return free_vars, exprs

def find_conditions(equations: List[Traced], conclusion, source):
    angle_linear, length_linear, length_ratio, others = classify_equations(equations)
    """Given sympified equations and conclusions, return a list of necessary conditions"""
    def try_find(equations, conclusion):
        variables = set()
        for eqn in equations:
            variables = variables.union(eqn.free_symbols)
        variables = {item: i for i, item in enumerate(list(variables))}
        mat = vectorize([item.expr for item in equations], variables, source)
        eq = vectorize([conclusion], variables, source)
        deps = traceback(mat, eq)
        return [equations[i] for i in deps]
    if source == "angle_linear":
        equations = angle_linear
    elif source == "length_linear":
        equations = length_linear
    else:
        assert source == "length_ratio"
        equations = length_ratio
    return try_find(equations, conclusion)


def vectorize(equations, variables, source):
    A = np.zeros(shape=(len(equations), len(variables)), dtype=np.float64)
    b = np.zeros(shape=(len(equations), 1), dtype=np.float64)
    if source in ("angle_linear", "length_linear"):
        for i, eqn in enumerate(equations):
            eqn = sympy.expand(eqn)
            assert isinstance(eqn, sympy.core.add.Add)
            for add_arg in eqn.args:
                if len(add_arg.args) == 0:
                    mul_args = [add_arg]
                else:
                    assert isinstance(add_arg, sympy.core.mul.Mul)
                    mul_args = add_arg.args
                factors = [item for item in mul_args if len(
                    item.free_symbols) == 0]
                factor = sympy.core.mul.Mul(*factors)
                symbols = [item for item in mul_args if len(
                    item.free_symbols) > 0]
                if len(symbols) == 0:
                    b[i, 0] = factor.evalf()
                else:
                    A[i, variables[symbols[0]]] = factor.evalf()
    else:
        assert source == "length_ratio"  # length=const or eqlength or eqlength ratio or lengthratio=const
        for i, eqn in enumerate(equations):
            if isinstance(eqn, sympy.core.add.Add):
                if len(eqn.args) > 2:
                    breakpoint()
                    assert False
                add_args = eqn.args
            else:
                add_args = [eqn]
            for j, add_arg in enumerate(add_args):
                if len(add_arg.args) > 0:
                    mul_args = add_arg.args
                else:
                    mul_args = [add_arg]
                for mul_arg in mul_args:
                    if len(mul_arg.free_symbols) == 0:
                        b[i, 0] = (-1)**j*math.log(abs(mul_arg))
                    else:
                        symbol = list(mul_arg.free_symbols)[0]
                        if "/" in str(mul_arg):
                            A[i, variables[symbol]] = (-1)**(j+1)
                        else:
                            A[i, variables[symbol]] = (-1)**j
    return np.concat([A, b], axis=1)


def traceback(augmented_A, e) -> list[str]:
    m, n = augmented_A.shape
    e = e[0]
    n = n-1

    model = gp.Model()
    model.setParam('OutputFlag', 0)

    x = model.addVars(m, lb=-GRB.INFINITY, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS, name="x")
    z = model.addVars(m, vtype=GRB.BINARY, name="z")

    model.setObjective(gp.quicksum(z[i] for i in range(m)), GRB.MINIMIZE)

    for i in range(n + 1):
        model.addConstr(gp.quicksum(augmented_A[j, i] * x[j] for j in range(m)) == e[i])

    M = 1e6
    for i in range(m):
        model.addConstr(x[i] <= M * z[i])
        model.addConstr(x[i] >= -M * z[i])

    model.optimize()

    if model.status != GRB.OPTIMAL:
        print("Optimization failed.")
        return []
    
    return [i for i in range(m) if z[i].x > 0]
