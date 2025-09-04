from __future__ import annotations

import copy
import re
import itertools

from sympy import Symbol
from pyeuclid.formalization.utils import sort_points, sort_cyclic_points, sort_point_groups, sort_cyclic_point_groups


class UnsupportedRelation(Exception):
    pass


relations = {}


def register(relation):
    name = relation.__name__.lower()
    relations[name] = relation
    return relation


class Point:
    def __init__(self, name: str):
        self.name = name
        assert not "_" in name
        
    def __str__(self):
        return self.name

    def __eq__(self, other):
        return str(self) == str(other)

    def __repr__(self):
        return str(self)

    def __hash__(self):
        return hash(str(self))


class Relation:
    def __init__(self):
        self.negated = False
        
    def get_points(self):
        points = []
        for v in vars(self).values():
            if isinstance(v, Point):
                points.append(v)
        return points

    def __str__(self):
        class_name = self.__class__.__name__
        points = self.get_points()
        args_name = ",".join([p.name for p in points])
        if self.negated:
            return f"Not({class_name}({args_name}))"
        else:
            return f"{class_name}({args_name})"

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return str(self) == str(other)

    def __hash__(self):
        return hash(str(self))


def Not(rel):
    rel = copy.copy(rel)
    rel.negated = not rel.negated
    return rel


def equal(*lst):
    result = []
    for i in range(len(lst)):
        for j in range(i+1, len(lst)):
            result.append(lst[i]-lst[j])
    return result


class Lt(Relation):
    def __init__(self, v1: Point, v2: Point):
        """
        Used for obtaining a canonical order of assignments
        """
        super().__init__()
        self.v1 = v1
        self.v2 = v2

def Leq(v1: Point, v2: Point):
    return Not(Lt(v2, v1))

class Equal(Relation):
    def __init__(self, v1: Point, v2: Point):
        super().__init__()
        self.v1, self.v2 = sort_points(v1, v2)

    def permutations(self):
        return [(self.v1, self.v2), (self.v2, self.v1)]


def Angle(p1: Point, p2: Point, p3: Point):
    if isinstance(p1, str):
        p1 = Point(p1)
    if isinstance(p2, str):
        p2 = Point(p2)
    if isinstance(p3, str):
        p3 = Point(p3)
    p1, p3 = sort_points(p1, p3)
    return Symbol(f"Angle_{p1}_{p2}_{p3}", non_negative=True)


def Length(p1: Point, p2: Point):
    if isinstance(p1, str):
        p1 = Point(p1)
    if isinstance(p2, str):
        p2 = Point(p2)
    p1, p2 = sort_points(p1, p2)
    return Symbol(f"Length_{str(p1)}_{str(p2)}", positive=True)


def Area(*ps: list[Point]):
    ps = sort_cyclic_points(*ps)
    return Symbol("_".join(["Area"] + [str(item) for item in ps]), positive=True)

def Variable(name: str):
    return Symbol(f"Variable_{name}")

def AreaOfCircle(center: Point, p1: Point):
    return Symbol(f"AreaOfCircle_{center}_{p1}")

def MajorSector(center: Point, p1: Point, p2: Point):
    p1, p2 = sort_points(p1, p2)
    return Symbol(f"MajorSector_{center}_{p1}_{p2}")
    
def MinorSector(center: Point, p1: Point, p2: Point):
    p1, p2 = sort_points(p1, p2)
    return Symbol(f"MinorSector_{center}_{p1}_{p2}")

def MajorArc(center: Point, p1: Point, p2: Point):
    p1, p2 = sort_points(p1, p2)
    return Symbol(f"MajorArc_{center}_{p1}_{p2}")
    
def MinorArc(center: Point, p1: Point, p2: Point):
    p1, p2 = sort_points(p1, p2)
    return Symbol(f"MinorArc_{center}_{p1}_{p2}")

def Perimeter(*ps: list[Point]):
    ps = sort_cyclic_points(*ps)
    return Symbol("_".join(["Perimeter"] + [str(item) for item in ps]), positive=True)

class Different2(Relation):
    def __init__(self, p1: Point, p2: Point):
        super().__init__()
        self.p1, self.p2 = sort_points(p1, p2)
    
    def permutations(self):
        return [(self.p1, self.p2), (self.p2, self.p1)]


def Different(*ps: Point):
    return [Different2(ps[i], ps[j]) for i in range(len(ps)) for j in range(i + 1, len(ps))]


@register
class Between(Relation):
    def __init__(self, p1: Point, p2: Point, p3: Point):
        """
        p1 is between p2 and p3.
        """
        super().__init__()
        p2, p3 = sort_points(p2, p3)
        self.p1, self.p2, self.p3 = p1, p2, p3

    def permutations(self):
        return [(self.p1, self.p2, self.p3), (self.p1, self.p3, self.p2)]


@register
class SameSide(Relation):
    def __init__(self, p1: Point, p2: Point, p3: Point, p4: Point):
        super().__init__()
        self.p1, self.p2 = sort_points(p1, p2)
        self.p3, self.p4 = sort_points(p3, p4)

    def permutations(self):
        return [
            (self.p1, self.p2, self.p3, self.p4),
            (self.p1, self.p2, self.p4, self.p3),
            (self.p2, self.p1, self.p3, self.p4),
            (self.p2, self.p1, self.p4, self.p3),
        ]

@register
class OppositeSide(Relation):
    def __init__(self, p1: Point, p2: Point, p3: Point, p4: Point):
        super().__init__()
        self.p1, self.p2 = sort_points(p1, p2)
        self.p3, self.p4 = sort_points(p3, p4)
    
    def permutations(self):
        return [
            (self.p1, self.p2, self.p3, self.p4),
            (self.p1, self.p2, self.p4, self.p3),
            (self.p2, self.p1, self.p3, self.p4),
            (self.p2, self.p1, self.p4, self.p3),
        ]


@register
class Collinear(Relation):
    def __init__(self, p1, p2, p3):
        super().__init__()
        self.p1, self.p2, self.p3 = sort_points(p1, p2, p3)

    def permutations(self):
        return itertools.permutations([self.p1, self.p2, self.p3])

def NotCollinear(*ps):
    return Not(Collinear(*ps))

@register
class Midpoint(Relation):
    def __init__(self, p1: Point, p2: Point, p3: Point):
        super().__init__()
        self.p1 = p1
        self.p2, self.p3 = sort_points(p2, p3)
    
    def permutations(self):
        return [(self.p1, self.p2, self.p3), (self.p1, self.p3, self.p2)]


def Congruent(*ps: list[Point]):
    if not len(ps) % 2 == 0:
        raise UnsupportedRelation(f"Unsupported number of points for a Congruent relation: {len(ps)}")
    
    num = len(ps) // 2
    if num not in [3, 4, 5]:
        raise UnsupportedRelation(f"Unsupported number of points for a Congruent relation: {len(ps)}")
    
    return globals()['Congruent'+str(num)](*ps)

@register
class Congruent3(Relation):
    def __init__(self, p1: Point, p2: Point, p3: Point, p4: Point, p5: Point, p6: Point):
        super().__init__()
        self.p1, self.p2, self.p3, self.p4, self.p5, self.p6 = sort_cyclic_point_groups([p1, p2, p3], [p4, p5, p6], mapping=True)
        
    def permutations(self):
        perm_group1 = [tuple(itertools.islice(itertools.cycle([self.p1, self.p2, self.p3]), i, i + 3)) for i in range(3)]
        perm_group1 += [tuple(reversed(perm)) for perm in perm_group1]
        perm_group2 = [tuple(itertools.islice(itertools.cycle([self.p4, self.p5, self.p6]), i, i + 3)) for i in range(3)]
        perm_group2 += [tuple(reversed(perm)) for perm in perm_group2]
        
        return [(*p, *q) for p, q in zip(perm_group1, perm_group2)] + [(*q, *p) for p, q in zip(perm_group1, perm_group2)]


class Congruent4(Relation):
    def __init__(self, p1: Point, p2: Point, p3: Point, p4: Point, p5: Point, p6: Point, p7: Point, p8: Point):
        super().__init__()
        self.p1, self.p2, self.p3, self.p4, self.p5, self.p6 = sort_cyclic_point_groups([p1, p2, p3, p4], [p5, p6, p7, p8], mapping=True)
    
    def permutations(self):
        perm_group1 = [tuple(itertools.islice(itertools.cycle([self.p1, self.p2, self.p3, self.p4]), i, i + 4)) for i in range(4)]
        perm_group1 += [tuple(reversed(perm)) for perm in perm_group1]
        perm_group2 = [tuple(itertools.islice(itertools.cycle([self.p5, self.p6, self.p7, self.p8]), i, i + 4)) for i in range(4)]
        perm_group2 += [tuple(reversed(perm)) for perm in perm_group2]
        
        return [(*p, *q) for p, q in zip(perm_group1, perm_group2)] + [(*q, *p) for p, q in zip(perm_group1, perm_group2)]


class Congruent5(Relation):
    def __init__(self, p1: Point, p2: Point, p3: Point, p4: Point, p5: Point, p6: Point, p7: Point, p8: Point, p9: Point, p10: Point):
        super().__init__()
        self.p1, self.p2, self.p3, self.p4, self.p5, self.p6 = sort_cyclic_point_groups([p1, p2, p3, p4, p5], [p6, p7, p8, p9, p10], mapping=True)
    
    def permutations(self):
        perm_group1 = [tuple(itertools.islice(itertools.cycle([self.p1, self.p2, self.p3, self.p4, self.p5]), i, i + 5)) for i in range(5)]
        perm_group1 += [tuple(reversed(perm)) for perm in perm_group1]
        perm_group2 = [tuple(itertools.islice(itertools.cycle([self.p6, self.p7, self.p8, self.p9, self.p10]), i, i + 5)) for i in range(5)]
        perm_group2 += [tuple(reversed(perm)) for perm in perm_group2]
        
        return [(*p, *q) for p, q in zip(perm_group1, perm_group2)] + [(*q, *p) for p, q in zip(perm_group1, perm_group2)]


def Similar(*ps: list[Point]):
    if not len(ps) % 2 == 0:
        raise UnsupportedRelation(f"Unsupported number of points for a Similar relation: {len(ps)}")
    
    num = len(ps) // 2
    if num not in [3, 4, 5]:
        raise UnsupportedRelation(f"Unsupported number of points for a Similar relation: {len(ps)}")
    
    return globals()['Similar'+str(num)](*ps)


@register
class Similar3(Relation):
    def __init__(self, p1: Point, p2: Point, p3: Point, p4: Point, p5: Point, p6: Point):
        super().__init__()
        self.p1, self.p2, self.p3, self.p4, self.p5, self.p6 = sort_cyclic_point_groups([p1, p2, p3], [p4, p5, p6], mapping=True)
    
    def permutations(self):
        perm_group1 = [tuple(itertools.islice(itertools.cycle([self.p1, self.p2, self.p3]), i, i + 3)) for i in range(3)]
        perm_group1 += [tuple(reversed(perm)) for perm in perm_group1]
        perm_group2 = [tuple(itertools.islice(itertools.cycle([self.p4, self.p5, self.p6]), i, i + 3)) for i in range(3)]
        perm_group2 += [tuple(reversed(perm)) for perm in perm_group2]
        
        return [(*p, *q) for p, q in zip(perm_group1, perm_group2)] + [(*q, *p) for p, q in zip(perm_group1, perm_group2)]

@register
class Similar4(Relation):
    def __init__(self, p1: Point, p2: Point, p3: Point, p4: Point, p5: Point, p6: Point, p7: Point, p8: Point):
        super().__init__()
        self.p1, self.p2, self.p3, self.p4, self.p5, self.p6, self.p7, self.p8 = sort_cyclic_point_groups([p1, p2, p3, p4], [p5, p6, p7, p8], mapping=True)
    
    def permutations(self):
        perm_group1 = [tuple(itertools.islice(itertools.cycle([self.p1, self.p2, self.p3, self.p4]), i, i + 4)) for i in range(4)]
        perm_group1 += [tuple(reversed(perm)) for perm in perm_group1]
        perm_group2 = [tuple(itertools.islice(itertools.cycle([self.p5, self.p6, self.p7, self.p8]), i, i + 4)) for i in range(4)]
        perm_group2 += [tuple(reversed(perm)) for perm in perm_group2]
        
        return [(*p, *q) for p, q in zip(perm_group1, perm_group2)] + [(*q, *p) for p, q in zip(perm_group1, perm_group2)]

Similar4P = Similar4

@register
class Similar5(Relation):
    def __init__(self, p1: Point, p2: Point, p3: Point, p4: Point, p5: Point, p6: Point, p7: Point, p8: Point, p9: Point, p10: Point):
        super().__init__()
        self.p1, self.p2, self.p3, self.p4, self.p5, self.p6, self.p7, self.p8, self.p9, self.p10 = sort_cyclic_point_groups([p1, p2, p3, p4, p5], [p6, p7, p8, p9, p10], mapping=True)
    
    def permutations(self):
        perm_group1 = [tuple(itertools.islice(itertools.cycle([self.p1, self.p2, self.p3, self.p4, self.p5]), i, i + 5)) for i in range(5)]
        perm_group1 += [tuple(reversed(perm)) for perm in perm_group1]
        perm_group2 = [tuple(itertools.islice(itertools.cycle([self.p6, self.p7, self.p8, self.p9, self.p10]), i, i + 5)) for i in range(5)]
        perm_group2 += [tuple(reversed(perm)) for perm in perm_group2]
        
        return [(*p, *q) for p, q in zip(perm_group1, perm_group2)] + [(*q, *p) for p, q in zip(perm_group1, perm_group2)]

Similar5P = Similar5

@register
class Concyclic(Relation):
    def __init__(self, p1, p2, p3, p4):
        super().__init__()
        self.p1, self.p2, self.p3, self.p4 = sort_points(p1, p2, p3, p4)

    def permutations(self):
        return itertools.permutations([self.p1, self.p2, self.p3, self.p4])


@register
class Parallel(Relation):
    def __init__(self, p1: Point, p2: Point, p3: Point, p4: Point):
        super().__init__()
        self.p1, self.p2, self.p3, self.p4 = sort_point_groups([p1, p2], [p3, p4])

    def permutations(self):
        return [
            (self.p1, self.p2, self.p3, self.p4),
            (self.p1, self.p2, self.p4, self.p3),
            (self.p2, self.p1, self.p3, self.p4),
            (self.p2, self.p1, self.p4, self.p3),
            (self.p3, self.p4, self.p1, self.p2),
            (self.p4, self.p3, self.p1, self.p2),
            (self.p3, self.p4, self.p2, self.p1),
            (self.p4, self.p3, self.p2, self.p1),
        ]

@register
class Perpendicular(Relation):
    def __init__(self, p1: Point, p2: Point, p3: Point, p4: Point):
        super().__init__()
        self.p1, self.p2, self.p3, self.p4 = sort_point_groups([p1, p2], [p3, p4])

    def permutations(self):
        return [
            (self.p1, self.p2, self.p3, self.p4),
            (self.p1, self.p2, self.p4, self.p3),
            (self.p2, self.p1, self.p3, self.p4),
            (self.p2, self.p1, self.p4, self.p3),
            (self.p3, self.p4, self.p1, self.p2),
            (self.p4, self.p3, self.p1, self.p2),
            (self.p3, self.p4, self.p2, self.p1),
            (self.p4, self.p3, self.p2, self.p1),
        ]

def Polygon(*ps: Point):
    if len(ps) == 3:
        return Triangle(*ps)
    elif len(ps) == 4:
        return Quadrilateral(*ps)
    elif len(ps) == 5:
        return Pentagon(*ps)
    elif len(ps) == 6:
        return Hexagon(*ps)
    elif len(ps) == 7:
        return Heptagon(*ps)
    elif len(ps) == 8:
        return Octagon(*ps)
    else:
        raise UnsupportedRelation(f"Unsupported number of points for a Polygon: {len(ps)}")

@register
class Triangle(Relation):
    def __init__(self, p1: Point, p2: Point, p3: Point):
        super().__init__()
        self.p1, self.p2, self.p3 = sort_points(p1, p2, p3)

    def permutations(self):
        return itertools.permutations([self.p1, self.p2, self.p3])


@register
class IsoscelesTriangle(Relation):
    def __init__(self, p1: Point, p2: Point, p3: Point):
        super().__init__()
        self.p1, self.p2, self.p3 = sort_points(p1, p2, p3)

    def permutations(self):
        return itertools.permutations([self.p1, self.p2, self.p3])
    

@register
class EquilateralTriangle(Relation):
    def __init__(self, p1: Point, p2: Point, p3: Point):
        super().__init__()
        self.p1, self.p2, self.p3 = sort_points(p1, p2, p3)

    def permutations(self):
        return itertools.permutations([self.p1, self.p2, self.p3])


@register
class Quadrilateral(Relation):
    def __init__(self, p1: Point, p2: Point, p3: Point, p4: Point):
        super().__init__()
        self.p1, self.p2, self.p3, self.p4 = sort_cyclic_points(p1, p2, p3, p4)

    def permutations(self):
        forward_permutations = [tuple(itertools.islice(itertools.cycle([self.p1, self.p2, self.p3, self.p4]), i, i + 4)) for i in range(4)]
        reverse_permutations = [tuple(reversed(perm)) for perm in forward_permutations]
        return forward_permutations + reverse_permutations

@register
class Pentagon(Relation):
    def __init__(self, p1: Point, p2: Point, p3: Point, p4: Point, p5: Point):
        super().__init__()
        self.p1, self.p2, self.p3, self.p4, self.p5 = sort_cyclic_points(p1, p2, p3, p4, p5)

    def permutations(self):
        forward_permutations = [tuple(itertools.islice(itertools.cycle([self.p1, self.p2, self.p3, self.p4, self.p5]), i, i + 5)) for i in range(5)]
        reverse_permutations = [tuple(reversed(perm)) for perm in forward_permutations]
        return forward_permutations + reverse_permutations


class Hexagon(Relation):
    def __init__(self, p1: Point, p2: Point, p3: Point, p4: Point, p5: Point, p6: Point):
        super().__init__()
        self.p1, self.p2, self.p3, self.p4, self.p5, self.p6 = sort_cyclic_points(p1, p2, p3, p4, p5, p6)

    def permutations(self):
        forward_permutations = [tuple(itertools.islice(itertools.cycle([self.p1, self.p2, self.p3, self.p4, self.p5, self.p6]), i, i + 6)) for i in range(6)]
        reverse_permutations = [tuple(reversed(perm)) for perm in forward_permutations]
        return forward_permutations + reverse_permutations


class Heptagon(Relation):
    def __init__(self, p1: Point, p2: Point, p3: Point, p4: Point, p5: Point, p6: Point, p7: Point):
        super().__init__()
        self.p1, self.p2, self.p3, self.p4, self.p5, self.p6, self.p7 = sort_cyclic_points(p1, p2, p3, p4, p5, p6, p7)

    def permutations(self):
        forward_permutations = [tuple(itertools.islice(itertools.cycle([self.p1, self.p2, self.p3, self.p4, self.p5, self.p6, self.p7]), i, i + 7)) for i in range(7)]
        reverse_permutations = [tuple(reversed(perm)) for perm in forward_permutations]
        return forward_permutations + reverse_permutations


class Octagon(Relation):
    def __init__(self, p1: Point, p2: Point, p3: Point, p4: Point, p5: Point, p6: Point, p7: Point, p8: Point):
        super().__init__()
        self.p1, self.p2, self.p3, self.p4, self.p5, self.p6, self.p7, self.p8 = sort_cyclic_points(p1, p2, p3, p4, p5, p6, p7, p8)

    def permutations(self):
        forward_permutations = [tuple(itertools.islice(itertools.cycle([self.p1, self.p2, self.p3, self.p4, self.p5, self.p6, self.p7, self.p8]), i, i + 8)) for i in range(8)]
        reverse_permutations = [tuple(reversed(perm)) for perm in forward_permutations]
        return forward_permutations + reverse_permutations


# def Regular(*ps: Point):
#     if len(ps) ==3
#     ps = obj.get_points()
#     if isinstance(obj, Triangle):
#         return EquilateralTriangle(*ps)
#     elif isinstance(obj, Quadrilateral):
#         return Square(*ps)
#     elif isinstance(obj, Pentagon):
#         return Regular5(*ps)
#     elif isinstance(obj, Hexagon):
#         return Regular6(*ps)
#     elif isinstance(obj, Heptagon):
#         return Regular7(*ps)
#     elif isinstance(obj, Octagon):
#         return Regular8(*ps)
#     else:
#         raise UnsupportedRelation(f"Unsupported number of points for a Regular Object: {len(ps)}")


class Regular5(Relation):
    def __init__(self, p1: Point, p2: Point, p3: Point, p4: Point, p5: Point):
        super().__init__()
        self.p1, self.p2, self.p3, self.p4, self.p5 = sort_cyclic_points(p1, p2, p3, p4, p5)

    def permutations(self):
        forward_permutations = [tuple(itertools.islice(itertools.cycle([self.p1, self.p2, self.p3, self.p4, self.p5]), i, i + 5)) for i in range(5)]
        reverse_permutations = [tuple(reversed(perm)) for perm in forward_permutations]
        return forward_permutations + reverse_permutations


class Regular6(Relation):
    def __init__(self, p1: Point, p2: Point, p3: Point, p4: Point, p5: Point, p6: Point):
        super().__init__()
        self.p1, self.p2, self.p3, self.p4, self.p5, self.p6 = sort_cyclic_points(p1, p2, p3, p4, p5, p6)

    def permutations(self):
        forward_permutations = [tuple(itertools.islice(itertools.cycle([self.p1, self.p2, self.p3, self.p4, self.p5, self.p6]), i, i + 6)) for i in range(6)]
        reverse_permutations = [tuple(reversed(perm)) for perm in forward_permutations]
        return forward_permutations + reverse_permutations


class Regular7(Relation):
    def __init__(self, p1: Point, p2: Point, p3: Point, p4: Point, p5: Point, p6: Point, p7: Point):
        super().__init__()
        self.p1, self.p2, self.p3, self.p4, self.p5, self.p6, self.p7 = sort_cyclic_points(p1, p2, p3, p4, p5, p6, p7)

    def permutations(self):
        forward_permutations = [tuple(itertools.islice(itertools.cycle([self.p1, self.p2, self.p3, self.p4, self.p5, self.p6, self.p7]), i, i + 7)) for i in range(7)]
        reverse_permutations = [tuple(reversed(perm)) for perm in forward_permutations]
        return forward_permutations + reverse_permutations


class Regular8(Relation):
    def __init__(self, p1: Point, p2: Point, p3: Point, p4: Point, p5: Point, p6: Point, p7: Point, p8: Point):
        super().__init__()
        self.p1, self.p2, self.p3, self.p4, self.p5, self.p6, self.p7, self.p8 = sort_cyclic_points(p1, p2, p3, p4, p5, p6, p7, p8)

    def permutations(self):
        forward_permutations = [tuple(itertools.islice(itertools.cycle([self.p1, self.p2, self.p3, self.p4, self.p5, self.p6, self.p7, self.p8]), i, i + 8)) for i in range(8)]
        reverse_permutations = [tuple(reversed(perm)) for perm in forward_permutations]
        return forward_permutations + reverse_permutations

@register
class Parallelogram(Relation):
    def __init__(self, p1: Point, p2: Point, p3: Point, p4: Point):
        super().__init__()
        self.p1, self.p2, self.p3, self.p4 = sort_cyclic_points(p1, p2, p3, p4)
    
    def permutations(self):
        forward_permutations = [tuple(itertools.islice(itertools.cycle([self.p1, self.p2, self.p3, self.p4]), i, i + 4)) for i in range(4)]
        reverse_permutations = [tuple(reversed(perm)) for perm in forward_permutations]
        return forward_permutations + reverse_permutations


@register
class Square(Relation):
    def __init__(self, p1: Point, p2: Point, p3: Point, p4: Point):
        super().__init__()
        self.p1, self.p2, self.p3, self.p4 = sort_cyclic_points(p1, p2, p3, p4)
    
    def permutations(self):
        forward_permutations = [tuple(itertools.islice(itertools.cycle([self.p1, self.p2, self.p3, self.p4]), i, i + 4)) for i in range(4)]
        reverse_permutations = [tuple(reversed(perm)) for perm in forward_permutations]
        return forward_permutations + reverse_permutations


@register
class Rectangle(Relation):
    def __init__(self, p1: Point, p2: Point, p3: Point, p4: Point):
        super().__init__()
        self.p1, self.p2, self.p3, self.p4 = sort_cyclic_points(p1, p2, p3, p4)
    
    def permutations(self):
        forward_permutations = [tuple(itertools.islice(itertools.cycle([self.p1, self.p2, self.p3, self.p4]), i, i + 4)) for i in range(4)]
        reverse_permutations = [tuple(reversed(perm)) for perm in forward_permutations]
        return forward_permutations + reverse_permutations


@register
class Rhombus(Relation):
    def __init__(self, p1: Point, p2: Point, p3: Point, p4: Point):
        super().__init__()
        self.p1, self.p2, self.p3, self.p4 = sort_cyclic_points(p1, p2, p3, p4)
    
    def permutations(self):
        forward_permutations = [tuple(itertools.islice(itertools.cycle([self.p1, self.p2, self.p3, self.p4]), i, i + 4)) for i in range(4)]
        reverse_permutations = [tuple(reversed(perm)) for perm in forward_permutations]
        return forward_permutations + reverse_permutations


@register
class Trapezoid(Relation):
    def __init__(self, p1: Point, p2: Point, p3: Point, p4: Point):
        super().__init__()
        self.p1, self.p2, self.p3, self.p4 = sort_cyclic_points(p1, p2, p3, p4)
    
    def permutations(self):
        forward_permutations = [tuple(itertools.islice(itertools.cycle([self.p1, self.p2, self.p3, self.p4]), i, i + 4)) for i in range(4)]
        reverse_permutations = [tuple(reversed(perm)) for perm in forward_permutations]
        return forward_permutations + reverse_permutations


@register
class EquilateralTrapezoid(Relation):
    def __init__(self, p1: Point, p2: Point, p3: Point, p4: Point):
        super().__init__()
        self.p1, self.p2, self.p3, self.p4 = sort_cyclic_points(p1, p2, p3, p4)
    
    def permutations(self):
        forward_permutations = [tuple(itertools.islice(itertools.cycle([self.p1, self.p2, self.p3, self.p4]), i, i + 4)) for i in range(4)]
        reverse_permutations = [tuple(reversed(perm)) for perm in forward_permutations]
        return forward_permutations + reverse_permutations


@register
class Kite(Relation):
    def __init__(self, p1: Point, p2: Point, p3: Point, p4: Point):
        super().__init__()
        self.p1, self.p2, self.p3, self.p4 = sort_cyclic_points(p1, p2, p3, p4)
    
    def permutations(self):
        forward_permutations = [tuple(itertools.islice(itertools.cycle([self.p1, self.p2, self.p3, self.p4]), i, i + 4)) for i in range(4)]
        reverse_permutations = [tuple(reversed(perm)) for perm in forward_permutations]
        return forward_permutations + reverse_permutations


@register
class Incenter(Relation):
    def __init__(self, o: Point, p1: Point, p2: Point, p3: Point):
        super().__init__()
        self.o = o
        self.p1, self.p2, self.p3 = sort_points(p1, p2, p3)
    
    def permutations(self):
        return [(self.o, *perm) for perm in itertools.permutations([self.p1, self.p2, self.p3])]


@register
class Centroid(Relation):
    def __init__(self, o: Point, p1: Point, p2: Point, p3: Point):
        super().__init__()
        self.o = o
        self.p1, self.p2, self.p3 = sort_points(p1, p2, p3)
    
    def permutations(self):
        return [(self.o, *perm) for perm in itertools.permutations([self.p1, self.p2, self.p3])]


@register
class Orthocenter(Relation):
    def __init__(self, o: Point, p1: Point, p2: Point, p3: Point):
        super().__init__()
        self.o = o
        self.p1, self.p2, self.p3 = sort_points(p1, p2, p3)
    
    def permutations(self):
        return [(self.o, *perm) for perm in itertools.permutations([self.p1, self.p2, self.p3])]


@register
class Circumcenter(Relation):
    def __init__(self, o: Point, p1: Point, p2: Point, p3: Point):
        super().__init__()
        self.o = o
        self.p1, self.p2, self.p3 = sort_points(p1, p2, p3)
    
    def permutations(self):
        return [(self.o, *perm) for perm in itertools.permutations([self.p1, self.p2, self.p3])]


@register
class Excenter(Relation):
    def __init__(self, o: Point, p1: Point, p2: Point, p3: Point):
        super().__init__()
        self.o = o
        self.p1, self.p2, self.p3 = sort_points(p1, p2, p3)
    
    def permutations(self):
        return [(self.o, *perm) for perm in itertools.permutations([self.p1, self.p2, self.p3])]


@register
class Acute(Relation):
    def __init__(self, p1: Point, p2: Point, p3: Point):
        super().__init__()
        p1, p3 = sort_points(p1, p3)
        self.p1, self.p2, self.p3 = p1, p2, p3
    
    def permutations(self):
        return [(self.p1, self.p2, self.p3), (self.p3, self.p2, self.p1)]


@register
class Obtuse(Relation):
    def __init__(self, p1: Point, p2: Point, p3: Point):
        super().__init__()
        p1, p3 = sort_points(p1, p3)
        self.p1, self.p2, self.p3 = p1, p2, p3
    
    def permutations(self):
        return [(self.p1, self.p2, self.p3), (self.p3, self.p2, self.p1)]


def trivial_condition(node):
    if isinstance(node, Relation) and node.negated:
        return True
    if isinstance(node, (Between, Acute, Obtuse, SameSide, OppositeSide, Lt, Different2, Triangle, Quadrilateral)):
        return True
    if isinstance(node, Collinear) and ((node.p1 == node.p2 or node.p2 == node.p3 or node.p3 == node.p1)):
        return True
    if node == 0: # Angle_a_b_c - Angle_c_b_a
        return True
    return False


def get_points_and_symbols(eqn):
    pattern = re.compile(r"((?:Angle|Length|Area|Variable)\w+)")
    # eqn.free_symbols is not apRelationoriate in this case, we need an ordered list instead of a set
    matches = pattern.findall(str(eqn))
    symbols = []
    points = []
    for match in matches:
        cls, args = match.split("_")[0], match.split("_")[1:]
        if cls == "Variable":
            arg = "_".join(match.split("_")[1:])
            symbol = Variable(arg)
        else:
            args = [Point(item) for item in args]
            if cls == "Angle":
                symbol = Angle(*args)
            elif cls == "Length":
                symbol = Length(*args)
            elif cls == "Area":
                symbol = Area(*args)
            points.append(args)
        symbols.append(symbol)
    return points, symbols
