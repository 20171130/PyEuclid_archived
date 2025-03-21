import re
import hashlib

from itertools import permutations, product
from collections import deque
from typing import List


def sort_attributes(*attrs):
    """
    Sort the list of attributes by their 'name'. The prop is unchanged when the order is changed
    e.g. Collinear(a,b,c)
    """

    return sorted(attrs, key=lambda i: i.name)

def sort_cyclic(*attrs):
    min_index = min(range(len(attrs)), key=lambda i: attrs[i].name)
    if str(attrs[(min_index+1) % len(attrs)]) > str(attrs[(min_index-1) % len(attrs)]):
        remaining_list = list(attrs[min_index:] + attrs[:min_index])[1:]
        return [attrs[min_index]] + remaining_list[::-1]
    else:
        return attrs[min_index:] + attrs[:min_index]
    

def compare_lists(L1, L2):
    for i in range(len(L1)):
        if L1[i].name < L2[i].name:
            return 0  # L1 < L2
        elif L1[i].name > L2[i].name:
            return 1  # L1 > L2
    return 0  # L1 == L2 (all elements are equal)


def get_cyclic_permutations(*attrs):
    permuted_instances = []

    # Generate cyclic permutations
    for _ in range(len(attrs)):
        attrs = deque(attrs)
        attrs.rotate(-1)  # Perform a left rotation
        permuted_instances.append(attrs)

    return list(permuted_instances)


def get_all_permutations(*attrs):
    return [perm for perm in permutations(attrs)]


def get_fixed_first_permutations(first, *rest):
    return [(first,) + perm for perm in permutations(rest)]


def get_double_angle_permutations(*attrs):
    a, b, c, d, e, f = attrs
    permuted_instances = []

    for perm in permutations([a,  c]):
        corresponding_points = {a: d, c: f}
        mapped = [perm[0], b, perm[1], corresponding_points[perm[0]],
                  e, corresponding_points[perm[1]]]
        permuted_instances.append(mapped)

    # Add swapped versions
    for perm in permutations([d, f]):
        corresponding_points = {d: a, f: c}
        mapped = [perm[0], e, perm[1], corresponding_points[perm[0]],
                  b, corresponding_points[perm[1]]]
        permuted_instances.append(mapped)

    return permuted_instances


def get_double_angle4_permutations(*attrs):
    a, b, c, d, e, f, g, h = attrs
    permuted_instances = []

    perms_ab = list(permutations([a, b]))
    perms_cd = list(permutations([c, d]))
    perms_ef = list(permutations([e, f]))
    perms_gh = list(permutations([g, h]))
    for perm_ab, perm_cd, perm_ef, perm_gh in product(perms_ab, perms_cd, perms_ef, perms_gh):
        permuted_instances.append(perm_ab + perm_cd + perm_ef + perm_gh)
        permuted_instances.append(perm_cd + perm_ab + perm_ef + perm_gh)
        permuted_instances.append(perm_cd + perm_ab + perm_gh + perm_ef)
        permuted_instances.append(perm_cd + perm_ab + perm_ef + perm_gh)
        permuted_instances.append(perm_ef + perm_gh + perm_ab + perm_cd)
        permuted_instances.append(perm_ef + perm_gh + perm_cd + perm_ab)
        permuted_instances.append(perm_gh + perm_ef + perm_cd + perm_ab)
        permuted_instances.append(perm_ef + perm_gh + perm_cd + perm_ab)
    return permuted_instances


def get_double_triangle_permutations(*attrs):
    a, b, c, d, e, f = attrs
    permuted_instances = []

    for perm in permutations([a, b, c]):
        corresponding_points = {a: d, b: e, c: f}
        mapped = [perm[0], perm[1], perm[2], corresponding_points[perm[0]],
                  corresponding_points[perm[1]], corresponding_points[perm[2]]]
        permuted_instances.append(mapped)

    # Add swapped versions
    for perm in permutations([d, e, f]):
        corresponding_points = {d: a, e: b, f: c}
        mapped = [perm[0], perm[1], perm[2], corresponding_points[perm[0]],
                  corresponding_points[perm[1]], corresponding_points[perm[2]]]
        permuted_instances.append(mapped)

    return permuted_instances


def get_double_lines_permutations(*attrs):
    a, b, c, d = attrs
    permuted_instances = []

    perms_ab = list(permutations([a, b]))
    perms_cd = list(permutations([c, d]))

    for perm_ab, perm_cd in product(perms_ab, perms_cd):
        permuted_instances.append(perm_ab + perm_cd)

    return permuted_instances


def expand(props):
    if not type(props) in (tuple, list):
        props = props,
    lst = []
    for prop in props:
        if hasattr(prop, "definition"):
            for item in prop.definition():
                lst += expand(item)
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


def parse_condition_conclusion(problem): 
    parts = problem.split(' ? ')
    if len(parts) > 1:
        return parts[0].strip()
    else:
        return problem.strip()


def generate_md5_filename(problem, extension=".pkl"):
    cond = parse_condition_conclusion(problem)
    hash_value = hashlib.md5(cond.encode('utf-8')).hexdigest()
    return f"{hash_value}{extension}"
