from __future__ import annotations

import copy
import re
import itertools

from sympy import Symbol, pi

from pyeuclid.formalization.utils import sort_points, sort_cyclic_points, sort_point_groups, get_point_mapping


class UnsupportedRelation(Exception):
    pass


relation_sets = {}


class register():
    def __init__(self, *annotations):
        self.annotations = annotations
    
    def __call__(self, cls):
        for item in self.annotations:
            if not item in relation_sets:
                relation_sets[item] = [cls]
            else:
                relation_sets[item].append(cls)


class Point():
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
        points = vars(self).values()
        assert all(isinstance(p, Point) for p in points)
        return list(points)

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


class Object(Relation):
    def __init__(self):
        super().__init__()


class Segment(Object):
    def __init__(self, a: Point, b: Point):
        super().__init__()
        self.a, self.b = sort_points(a, b)
    
    def permutations(self):
        return [(self.a, self.b), (self.b, self.a)]


class Circle(Object):
    def __init__(self, o: Point):
        super().__init__()
        self.o = o
    
    def permutations(self):
        return [(self.o)]


class Angle(Object):
    def __init__(self, a: Point, b: Point, c: Point):
        super().__init__()
        a, c = sort_points(a, c)
        self.a = a
        self.b = b
        self.c = c
    
    def permutations(self):
        return [(self.a, self.b, self.c), (self.c, self.b, self.a)]


class Arc(Object):
    def __init__(self, a: Point, o: Point, b: Point):
        super().__init__()
        a, b = sort_points(a, b)
        self.a, self.o, self.b = a, o, b
    
    def permutations(self):
        return [(self.a, self.o, self.b), (self.b, self.o, self.a)]


class Sector(Object):
    def __init__(self, a: Point, o: Point, b: Point):
        super().__init__()
        a, b = sort_points(a, b)
        self.a, self.o, self.b = a, o, b
    
    def permutations(self):
        return [(self.a, self.o, self.b), (self.b, self.o, self.a)]


class Triangle(Object):
    def __init__(self, p1: Point, p2: Point, p3: Point):
        super().__init__()
        self.p1, self.p2, self.p3 = sort_points(p1, p2, p3)

    def permutations(self):
        return itertools.permutations([self.p1, self.p2, self.p3])


class IsoscelesTriangle(Triangle):
    def __init__(self, p1: Point, p2: Point, p3: Point):
        super().__init__()
        p2, p3 = sort_points(p2, p3)
        self.p1, self.p2, self.p3 = p1, p2, p3

    def permutations(self):
        return [(self.p1, self.p2, self.p3), (self.p1, self.p3, self.p2)]
    

class EquilateralTriangle(Triangle):
    def __init__(self, p1: Point, p2: Point, p3: Point):
        super().__init__()
        self.p1, self.p2, self.p3 = sort_points(p1, p2, p3)

    def permutations(self):
        return itertools.permutations([self.p1, self.p2, self.p3])
    

class RightTriangle(Triangle):
    def __init__(self, p1: Point, p2: Point, p3: Point):
        super().__init__()
        p1, p3 = sort_points(p1, p3)
        self.p1, self.p2, self.p3 = p1, p2, p3

    def permutations(self):
        return [(self.p1, self.p2, self.p3), (self.p3, self.p2, self.p1)]


class Quadrilateral(Object):
    def __init__(self, p1: Point, p2: Point, p3: Point, p4: Point):
        super().__init__()
        self.p1, self.p2, self.p3, self.p4 = sort_cyclic_points(p1, p2, p3, p4)

    def permutations(self):
        forward_permutations = [tuple(itertools.islice(itertools.cycle([self.p1, self.p2, self.p3, self.p4]), i, i + 4)) for i in range(4)]
        reverse_permutations = [tuple(reversed(perm)) for perm in forward_permutations]
        return forward_permutations + reverse_permutations


class Parallelogram(Quadrilateral):
    def __init__(self, p1: Point, p2: Point, p3: Point, p4: Point):
        super().__init__()
        self.p1, self.p2, self.p3, self.p4 = sort_cyclic_points(p1, p2, p3, p4)
    
    def permutations(self):
        forward_permutations = [tuple(itertools.islice(itertools.cycle([self.p1, self.p2, self.p3, self.p4]), i, i + 4)) for i in range(4)]
        reverse_permutations = [tuple(reversed(perm)) for perm in forward_permutations]
        return forward_permutations + reverse_permutations

    # def definition(self):
    #     return [
    #         Parallel(self.p1, self.p2, self.p3, self.p4),
    #         Parallel(self.p2, self.p3, self.p4, self.p1),
    #         Quadrilateral(self.p1, self.p2, self.p3, self.p4),
    #     ]


class Square(Quadrilateral):
    def __init__(self, p1: Point, p2: Point, p3: Point, p4: Point):
        super().__init__()
        self.p1, self.p2, self.p3, self.p4 = sort_cyclic_points(p1, p2, p3, p4)
    
    def permutations(self):
        forward_permutations = [tuple(itertools.islice(itertools.cycle([self.p1, self.p2, self.p3, self.p4]), i, i + 4)) for i in range(4)]
        reverse_permutations = [tuple(reversed(perm)) for perm in forward_permutations]
        return forward_permutations + reverse_permutations

    # def definition(self):
    #     return [
    #         Length(self.p1, self.p2) - Length(self.p2, self.p3),
    #         Length(self.p2, self.p3) - Length(self.p3, self.p4),
    #         Length(self.p3, self.p4) - Length(self.p4, self.p1),
    #         Length(self.p4, self.p1) - Length(self.p1, self.p2),
    #         Angle(self.p1, self.p2, self.p3) - pi / 2,
    #         Angle(self.p2, self.p3, self.p4) - pi / 2,
    #         Angle(self.p3, self.p4, self.p1) - pi / 2,
    #         Angle(self.p4, self.p1, self.p2) - pi / 2,
    #         Quadrilateral(self.p1, self.p2, self.p3, self.p4),
    #     ]


class Rectangle(Quadrilateral):
    def __init__(self, p1: Point, p2: Point, p3: Point, p4: Point):
        super().__init__()
        self.p1, self.p2, self.p3, self.p4 = sort_cyclic_points(p1, p2, p3, p4)
    
    def permutations(self):
        forward_permutations = [tuple(itertools.islice(itertools.cycle([self.p1, self.p2, self.p3, self.p4]), i, i + 4)) for i in range(4)]
        reverse_permutations = [tuple(reversed(perm)) for perm in forward_permutations]
        return forward_permutations + reverse_permutations

    # def definition(self):
    #     return [
    #         Length(self.p1, self.p2) - Length(self.p3, self.p4),
    #         Length(self.p2, self.p3) - Length(self.p4, self.p1),
    #         Angle(self.p1, self.p2, self.p3) - pi / 2,
    #         Angle(self.p2, self.p3, self.p4) - pi / 2,
    #         Angle(self.p3, self.p4, self.p1) - pi / 2,
    #         Angle(self.p4, self.p1, self.p2) - pi / 2,
    #         Quadrilateral(self.p1, self.p2, self.p3, self.p4),
    #     ]


class Rhombus(Quadrilateral):
    def __init__(self, p1: Point, p2: Point, p3: Point, p4: Point):
        super().__init__()
        self.p1, self.p2, self.p3, self.p4 = sort_cyclic_points(p1, p2, p3, p4)
    
    def permutations(self):
        forward_permutations = [tuple(itertools.islice(itertools.cycle([self.p1, self.p2, self.p3, self.p4]), i, i + 4)) for i in range(4)]
        reverse_permutations = [tuple(reversed(perm)) for perm in forward_permutations]
        return forward_permutations + reverse_permutations

    # def definition(self):
    #     return [
    #         Length(self.p1, self.p2) - Length(self.p2, self.p3),
    #         Length(self.p2, self.p3) - Length(self.p3, self.p4),
    #         Length(self.p3, self.p4) - Length(self.p4, self.p1),
    #         Length(self.p4, self.p1) - Length(self.p1, self.p2),
    #         Perpendicular(self.p1, self.p3, self.p2, self.p4),
    #         Quadrilateral(self.p1, self.p2, self.p3, self.p4),
    #     ]


class Trapezoid(Quadrilateral):
    def __init__(self, p1: Point, p2: Point, p3: Point, p4: Point):
        super().__init__()
        group1, group2 = map(sort_points, [[p1, p2], [p3, p4]])
        mapping = get_point_mapping([p1, p2], [p3, p4])
        self.p1, self.p2, self.p3, self.p4 = sort_point_groups(group1, group2, mapping)
    
    def permutations(self):
        return [
            (self.p1, self.p2, self.p3, self.p4),
            (self.p3, self.p4, self.p1, self.p2),
            (self.p4, self.p3, self.p2, self.p1),
            (self.p2, self.p1, self.p4, self.p3),
        ]

    # def definition(self):
    #     return [
    #         Parallel(self.p1, self.p2, self.p3, self.p4),
    #         Quadrilateral(self.p1, self.p2, self.p3, self.p4),
    #     ]


class Kite(Quadrilateral):
    def __init__(self, p1: Point, p2: Point, p3: Point, p4: Point):
        super().__init__()
        group1, group2 = map(sort_points, [[p1, p3], [p2, p4]])
        self.p1, self.p2, self.p3, self.p4 = group1[0], group2[0], group1[1], group2[1]
    
    def permutations(self):
        return [
            (self.p1, self.p2, self.p3, self.p4),
            (self.p1, self.p4, self.p3, self.p2),
            (self.p3, self.p2, self.p1, self.p4),
            (self.p3, self.p4, self.p1, self.p2),
        ]

    # def definition(self):
    #     return [
    #         Length(self.p1, self.p2) - Length(self.p2, self.p3),
    #         Length(self.p3, self.p4) - Length(self.p4, self.p1),
    #         Angle(self.p2, self.p1, self.p4) - Angle(self.p2, self.p3, self.p4),
    #         Angle(self.p1, self.p2, self.p3) - Angle(self.p1, self.p4, self.p3),
    #         Different(self.p1, self.p2, self.p3, self.p4),
    #         Perpendicular(self.p1, self.p3, self.p2, self.p4),
    #         Quadrilateral(self.p1, self.p2, self.p3, self.p4),
    #     ]


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


class Pentagon(Object):
    def __init__(self, p1: Point, p2: Point, p3: Point, p4: Point, p5: Point):
        super().__init__()
        self.p1, self.p2, self.p3, self.p4, self.p5 = sort_cyclic_points(p1, p2, p3, p4, p5)

    def permutations(self):
        forward_permutations = [tuple(itertools.islice(itertools.cycle([self.p1, self.p2, self.p3, self.p4, self.p5]), i, i + 5)) for i in range(5)]
        reverse_permutations = [tuple(reversed(perm)) for perm in forward_permutations]
        return forward_permutations + reverse_permutations


class Hexagon(Object):
    def __init__(self, p1: Point, p2: Point, p3: Point, p4: Point, p5: Point, p6: Point):
        super().__init__()
        self.p1, self.p2, self.p3, self.p4, self.p5, self.p6 = sort_cyclic_points(p1, p2, p3, p4, p5, p6)

    def permutations(self):
        forward_permutations = [tuple(itertools.islice(itertools.cycle([self.p1, self.p2, self.p3, self.p4, self.p5, self.p6]), i, i + 6)) for i in range(6)]
        reverse_permutations = [tuple(reversed(perm)) for perm in forward_permutations]
        return forward_permutations + reverse_permutations


class Heptagon(Object):
    def __init__(self, p1: Point, p2: Point, p3: Point, p4: Point, p5: Point, p6: Point, p7: Point):
        super().__init__()
        self.p1, self.p2, self.p3, self.p4, self.p5, self.p6, self.p7 = sort_cyclic_points(p1, p2, p3, p4, p5, p6, p7)

    def permutations(self):
        forward_permutations = [tuple(itertools.islice(itertools.cycle([self.p1, self.p2, self.p3, self.p4, self.p5, self.p6, self.p7]), i, i + 7)) for i in range(7)]
        reverse_permutations = [tuple(reversed(perm)) for perm in forward_permutations]
        return forward_permutations + reverse_permutations


class Octagon(Object):
    def __init__(self, p1: Point, p2: Point, p3: Point, p4: Point, p5: Point, p6: Point, p7: Point, p8: Point):
        super().__init__()
        self.p1, self.p2, self.p3, self.p4, self.p5, self.p6, self.p7, self.p8 = sort_cyclic_points(p1, p2, p3, p4, p5, p6, p7, p8)

    def permutations(self):
        forward_permutations = [tuple(itertools.islice(itertools.cycle([self.p1, self.p2, self.p3, self.p4, self.p5, self.p6, self.p7, self.p8]), i, i + 8)) for i in range(8)]
        reverse_permutations = [tuple(reversed(perm)) for perm in forward_permutations]
        return forward_permutations + reverse_permutations
    

class RightAngle(Relation):
    def __init__(self, p1: Point, p2: Point, p3: Point):
        super().__init__()
        p1, p3 = sort_points(p1, p3)
        self.p1, self.p2, self.p3 = p1, p2, p3

    def permutations(self):
        return [(self.p1, self.p2, self.p3), (self.p3, self.p2, self.p1)]


class Right(Relation):
    def __init__(self, p1: Point, p2: Point, p3: Point):
        super().__init__()
        p1, p3 = sort_points(p1, p3)
        self.p1, self.p2, self.p3 = p1, p2, p3

    def permutations(self):
        return [(self.p1, self.p2, self.p3), (self.p3, self.p2, self.p1)]


class Isosceles3(Relation):
    def __init__(self, p1: Point, p2: Point, p3: Point):
        super().__init__()
        p2, p3 = sort_points(p1, p3)
        self.p1, self.p2, self.p3 = p1, p2, p3

    def permutations(self):
        return [(self.p1, self.p2, self.p3), (self.p1, self.p3, self.p2)]
    

class Equilateral3(Relation):
    def __init__(self, p1: Point, p2: Point, p3: Point):
        super().__init__()
        self.p1, self.p2, self.p3 = sort_points(p1, p2, p3)

    def permutations(self):
        return itertools.permutations([self.p1, self.p2, self.p3])


def Regular(obj: Object):
    ps = obj.get_points()
    if isinstance(obj, Triangle):
        return EquilateralTriangle(*ps)
    elif isinstance(obj, Quadrilateral):
        return Square(*ps)
    elif isinstance(obj, Pentagon):
        return Regular5(*ps)
    elif isinstance(obj, Hexagon):
        return Regular6(*ps)
    elif isinstance(obj, Heptagon):
        return Regular7(*ps)
    elif isinstance(obj, Octagon):
        return Regular8(*ps)
    else:
        raise UnsupportedRelation(f"Unsupported number of points for a Regular Object: {len(ps)}")


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
    

def Not(rel):
    rel = copy.copy(rel)
    rel.negated = not rel.negated
    return rel


class Lt(Relation):
    def __init__(self, p1: Point, p2: Point):
        super().__init__()
        self.p1 = p1
        self.p2 = p2
    
    def permutations(self):
        return [(self.p1, self.p2)]


class Equal2(Relation):
    def __init__(self, p1: Point, p2: Point):
        super().__init__()
        self.p1, self.p2 = sort_points(p1, p2)

    def permutations(self):
        return [(self.p1, self.p2), (self.p2, self.p1)]


def Equal(*ps: list[Point]):
    return [Equal2(ps[i], ps[j]) for i in range(len(ps)) for j in range(len(i+1), len(ps))]


class Different2(Relation):
    def __init__(self, p1: Point, p2: Point):
        super().__init__()
        self.p1, self.p2 = sort_points(p1, p2)
    
    def permutations(self):
        return [(self.p1, self.p2), (self.p2, self.p1)]


def Different(*ps: list[Point]):
    return [Different2(ps[i], ps[j]) for i in range(len(ps)) for j in range(len(i+1), len(ps))]


class Between(Relation):
    def __init__(self, p1: Point, p2: Point, p3: Point):
        super().__init__()
        p2, p3 = sort_points(p2, p3)
        self.p1, self.p2, self.p3 = p1, p2, p3

    def permutations(self):
        return [(self.p1, self.p2, self.p3), (self.p1, self.p3, self.p2)]


class SameSide(Relation):
    def __init__(self, p1: Point, p2: Point, p3: Point, p4: Point):
        super().__init__()
        self.p1, self.p2 = sort_points(p1, p2)
        self.p3, self.p4 = sort_points(p3, p4)

    def permutations(self):
        return [
            (self.p1, self.p2, self.p3, self.p4),
            (self.p2, self.p1, self.p3, self.p4),
            (self.p1, self.p2, self.p4, self.p3),
            (self.p2, self.p1, self.p4, self.p3),
        ]


class OppositeSide(Relation):
    def __init__(self, p1: Point, p2: Point, p3: Point, p4: Point):
        super().__init__()
        self.p1, self.p2 = sort_points(p1, p2)
        self.p3, self.p4 = sort_points(p3, p4)
    
    def permutations(self):
        return [
            (self.p1, self.p2, self.p3, self.p4),
            (self.p2, self.p1, self.p3, self.p4),
            (self.p1, self.p2, self.p4, self.p3),
            (self.p2, self.p1, self.p4, self.p3),
        ]

    # def definition(self):
    #     return [
    #         Not(Collinear(self.p1, self.p3, self.p4)),
    #         Not(Collinear(self.p2, self.p3, self.p4)),
    #         Not(SameSide(self.p1, self.p2, self.p3, self.p4)),
    #     ]


class Collinear(Relation):
    def __init__(self, p1, p2, p3):
        super().__init__()
        self.p1, self.p2, self.p3 = sort_points(p1, p2, p3)

    def permutations(self):
        return itertools.permutations([self.p1, self.p2, self.p3])


# class NotCollinear(Relation):
#     def __init__(self, p1, p2, p3):
#         super().__init__()
#         self.p1, self.p2, self.p3 = sort_points(p1, p2, p3)

#     def definition(self):
#         return [
#             Not(Collinear(self.p1, self.p2, self.p3)),
#             Different(self.p1, self.p2, self.p3)
#         ]

    
def Congruent(*ps: list[Point]):
    if not len(ps) % 2 == 0:
        raise UnsupportedRelation(f"Unsupported number of points for a Congruent relation: {len(ps)}")
    
    num = len(ps) // 2
    if num not in [3, 4, 5]:
        raise UnsupportedRelation(f"Unsupported number of points for a Congruent relation: {len(ps)}")
    
    return globals()['Congruent'+str(num)](*ps)


class Congruent3(Relation):
    def __init__(self, p1: Point, p2: Point, p3: Point, p4: Point, p5: Point, p6: Point):
        super().__init__()
        group1, group2 = map(sort_points, [[p1, p2, p3], [p4, p5, p6]])
        mapping = get_point_mapping([p1, p2, p3], [p4, p5, p6])
        self.p1, self.p2, self.p3, self.p4, self.p5, self.p6 = sort_point_groups(group1, group2, mapping)
    
    def permutations(self):
        perm_group1 = [tuple(itertools.islice(itertools.cycle([self.p1, self.p2, self.p3]), i, i + 3)) for i in range(3)]
        perm_group1 += [tuple(reversed(perm)) for perm in perm_group1]
        perm_group2 = [tuple(itertools.islice(itertools.cycle([self.p4, self.p5, self.p6]), i, i + 3)) for i in range(3)]
        perm_group2 += [tuple(reversed(perm)) for perm in perm_group2]
        
        return [(*p, *q) for p, q in zip(perm_group1, perm_group2)] + [(*q, *p) for p, q in zip(perm_group1, perm_group2)]


class Congruent4(Relation):
    def __init__(self, p1: Point, p2: Point, p3: Point, p4: Point, p5: Point, p6: Point, p7: Point, p8: Point):
        super().__init__()
        group1, group2 = map(sort_points, [[p1, p2, p3, p4], [p5, p6, p7, p8]])
        mapping = get_point_mapping([p1, p2, p3, p4], [p5, p6, p7, p8])
        self.p1, self.p2, self.p3, self.p4, self.p5, self.p6, self.p7, self.p8 = sort_point_groups(group1, group2, mapping)
    
    def permutations(self):
        perm_group1 = [tuple(itertools.islice(itertools.cycle([self.p1, self.p2, self.p3, self.p4]), i, i + 4)) for i in range(4)]
        perm_group1 += [tuple(reversed(perm)) for perm in perm_group1]
        perm_group2 = [tuple(itertools.islice(itertools.cycle([self.p5, self.p6, self.p7, self.p8]), i, i + 4)) for i in range(4)]
        perm_group2 += [tuple(reversed(perm)) for perm in perm_group2]
        
        return [(*p, *q) for p, q in zip(perm_group1, perm_group2)] + [(*q, *p) for p, q in zip(perm_group1, perm_group2)]

    # def definition(self):
    #     return [
    #         Length(self.p1, self.p2) - Length(self.p4, self.p5),
    #         Length(self.p2, self.p3) - Length(self.p5, self.p6),
    #         Length(self.p1, self.p3) - Length(self.p4, self.p6),
    #         NotCollinear(self.p1, self.p2, self.p3),
    #     ]


class Congruent5(Relation):
    def __init__(self, p1: Point, p2: Point, p3: Point, p4: Point, p5: Point, p6: Point, p7: Point, p8: Point, p9: Point, p10: Point):
        super().__init__()
        group1, group2 = map(sort_points, [[p1, p2, p3, p4, p5], [p6, p7, p8, p9, p10]])
        mapping = get_point_mapping([p1, p2, p3, p4, p5], [p6, p7, p8, p9, p10])
        self.p1, self.p2, self.p3, self.p4, self.p5, self.p6, self.p7, self.p8, self.p9, self.p10 = sort_point_groups(group1, group2, mapping)
    
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


class Similar3(Relation):
    def __init__(self, p1: Point, p2: Point, p3: Point, p4: Point, p5: Point, p6: Point):
        super().__init__()
        group1, group2 = map(sort_points, [[p1, p2, p3], [p4, p5, p6]])
        mapping = get_point_mapping([p1, p2, p3], [p4, p5, p6])
        self.p1, self.p2, self.p3, self.p4, self.p5, self.p6 = sort_point_groups(group1, group2, mapping)
    
    def permutations(self):
        perm_group1 = [tuple(itertools.islice(itertools.cycle([self.p1, self.p2, self.p3]), i, i + 3)) for i in range(3)]
        perm_group1 += [tuple(reversed(perm)) for perm in perm_group1]
        perm_group2 = [tuple(itertools.islice(itertools.cycle([self.p4, self.p5, self.p6]), i, i + 3)) for i in range(3)]
        perm_group2 += [tuple(reversed(perm)) for perm in perm_group2]
        
        return [(*p, *q) for p, q in zip(perm_group1, perm_group2)] + [(*q, *p) for p, q in zip(perm_group1, perm_group2)]
    
    # def definition(self):
    #     return [
    #         Length(self.p1, self.p2) / Length(self.p4, self.p5)
    #         - Length(self.p2, self.p3) / Length(self.p5, self.p6),
    #         Length(self.p1, self.p2) / Length(self.p4, self.p5)
    #         - Length(self.p3, self.p1) / Length(self.p6, self.p4),
    #         NotCollinear(self.p1, self.p2, self.p3),
    #     ]

class Similar4(Relation):
    def __init__(self, p1: Point, p2: Point, p3: Point, p4: Point, p5: Point, p6: Point, p7: Point, p8: Point):
        super().__init__()
        group1, group2 = map(sort_points, [[p1, p2, p3, p4], [p5, p6, p7, p8]])
        mapping = get_point_mapping([p1, p2, p3, p4], [p5, p6, p7, p8])
        self.p1, self.p2, self.p3, self.p4, self.p5, self.p6, self.p7, self.p8 = sort_point_groups(group1, group2, mapping)
    
    def permutations(self):
        perm_group1 = [tuple(itertools.islice(itertools.cycle([self.p1, self.p2, self.p3, self.p4]), i, i + 4)) for i in range(4)]
        perm_group1 += [tuple(reversed(perm)) for perm in perm_group1]
        perm_group2 = [tuple(itertools.islice(itertools.cycle([self.p5, self.p6, self.p7, self.p8]), i, i + 4)) for i in range(4)]
        perm_group2 += [tuple(reversed(perm)) for perm in perm_group2]
        
        return [(*p, *q) for p, q in zip(perm_group1, perm_group2)] + [(*q, *p) for p, q in zip(perm_group1, perm_group2)]
    
        # def definition(self):
    #     return [
    #         Length(self.p1, self.p2) / Length(self.p5, self.p6)
    #         - Length(self.p2, self.p3) / Length(self.p6, self.p7),
    #         Length(self.p1, self.p2) / Length(self.p5, self.p6)
    #         - Length(self.p3, self.p4) / Length(self.p7, self.p8),
    #         Length(self.p1, self.p2) / Length(self.p5, self.p6)
    #         - Length(self.p4, self.p1) / Length(self.p8, self.p5),
    #         Angle(self.p1, self.p2, self.p3) - Angle(self.p5, self.p6, self.p7),
    #         Angle(self.p2, self.p3, self.p4) - Angle(self.p6, self.p7, self.p8),
    #         Angle(self.p3, self.p4, self.p1) - Angle(self.p7, self.p8, self.p5),
    #         Angle(self.p4, self.p1, self.p2) - Angle(self.p8, self.p5, self.p6),
    #     ]


class Similar5(Relation):
    def __init__(self, p1: Point, p2: Point, p3: Point, p4: Point, p5: Point, p6: Point, p7: Point, p8: Point, p9: Point, p10: Point):
        super().__init__()
        group1, group2 = map(sort_points, [[p1, p2, p3, p4, p5], [p6, p7, p8, p9, p10]])
        mapping = get_point_mapping([p1, p2, p3, p4, p5], [p6, p7, p8, p9, p10])
        self.p1, self.p2, self.p3, self.p4, self.p5, self.p6, self.p7, self.p8, self.p9, self.p10 = sort_point_groups(group1, group2, mapping)
    
    def permutations(self):
        perm_group1 = [tuple(itertools.islice(itertools.cycle([self.p1, self.p2, self.p3, self.p4, self.p5]), i, i + 5)) for i in range(5)]
        perm_group1 += [tuple(reversed(perm)) for perm in perm_group1]
        perm_group2 = [tuple(itertools.islice(itertools.cycle([self.p6, self.p7, self.p8, self.p9, self.p10]), i, i + 5)) for i in range(5)]
        perm_group2 += [tuple(reversed(perm)) for perm in perm_group2]
        
        return [(*p, *q) for p, q in zip(perm_group1, perm_group2)] + [(*q, *p) for p, q in zip(perm_group1, perm_group2)]

    # def definition(self):
    #     return [
    #         Length(self.p1, self.p2) / Length(self.p6, self.p7)
    #         - Length(self.p2, self.p3) / Length(self.p7, self.p8),
    #         Length(self.p2, self.p3) / Length(self.p7, self.p8)
    #         - Length(self.p3, self.p4) / Length(self.p8, self.p9),
    #         Length(self.p3, self.p4) / Length(self.p8, self.p9)
    #         - Length(self.p4, self.p5) / Length(self.p9, self.p10),
    #         Length(self.p4, self.p5) / Length(self.p9, self.p10)
    #         - Length(self.p5, self.p1) / Length(self.p10, self.p6),
    #         Length(self.p5, self.p1) / Length(self.p10, self.p6)
    #         - Length(self.p1, self.p2) / Length(self.p6, self.p7),
    #         Angle(self.p1, self.p2, self.p3) - Angle(self.p6, self.p7, self.p8),
    #         Angle(self.p2, self.p3, self.p4) - Angle(self.p7, self.p8, self.p9),
    #         Angle(self.p3, self.p4, self.p5) - Angle(self.p8, self.p9, self.p10),
    #         Angle(self.p4, self.p5, self.p1) - Angle(self.p9, self.p10, self.p6),
    #         Angle(self.p5, self.p1, self.p2) - Angle(self.p10, self.p6, self.p7),
    #     ]


class Concyclic(Relation):
    def __init__(self, p1, p2, p3, p4):
        super().__init__()
        self.p1, self.p2, self.p3, self.p4 = sort_points(p1, p2, p3, p4)

    def permutations(self):
        return itertools.permutations([self.p1, self.p2, self.p3, self.p4])


class Parallel(Relation):
    def __init__(self, p1: Point, p2: Point, p3: Point, p4: Point):
        super().__init__()
        p1, p2 = sort_points(p1, p2)
        p3, p4 = sort_points(p3, p4)
        self.p1, self.p2, self.p3, self.p4 = sort_point_groups([p1, p2], [p3, p4])

    def permutations(self):
        perm_group1 = list(itertools.permutations([self.p1, self.p2]))
        perm_group2 = list(itertools.permutations([self.p3, self.p4]))
        return [(*p, *q) for p in perm_group1 for q in perm_group2] + [(*q, *p) for p in perm_group1 for q in perm_group2]


class Perpendicular(Relation):
    def __init__(self, p1: Point, p2: Point, p3: Point, p4: Point):
        super().__init__()
        p1, p2 = sort_points(p1, p2)
        p3, p4 = sort_points(p3, p4)
        self.p1, self.p2, self.p3, self.p4 = sort_point_groups([p1, p2], [p3, p4])

    def permutations(self):
        perm_group1 = list(itertools.permutations([self.p1, self.p2]))
        perm_group2 = list(itertools.permutations([self.p3, self.p4]))
        return [(*p, *q) for p in perm_group1 for q in perm_group2] + [(*q, *p) for p in perm_group1 for q in perm_group2]
    

class IsMidpointOf(Relation):
    def __init__(self, p1: Point, p2: Point, p3: Point):
        super().__init__()
        self.p1 = p1
        self.p2, self.p3 = sort_points(p2, p3)
    
    def permutations(self):
        return [(self.p1, self.p2, self.p3), (self.p1, self.p3, self.p2)]

    # def definition(self):
    #     return [
    #         Length(self.p1, self.p2) - Length(self.p1, self.p3),
    #         Collinear(self.p1, self.p2, self.p3),
    #         Different(self.p2, self.p3),
    #         Between(self.p1, self.p2, self.p3),
    #     ]


class IsCentroidOf(Relation):
    def __init__(self, o: Point, p1: Point, p2: Point, p3: Point):
        super().__init__()
        self.o = o
        self.p1, self.p2, self.p3 = sort_points(p1, p2, p3)
    
    def permutations(self):
        return [(self.o, *perm) for perm in itertools.permutations([self.p1, self.p2, self.p3])]

    # def definition(self):
    #     return [
    #         Midpoint(self.d, self.b, self.c),
    #         Midpoint(self.e, self.a, self.c),
    #         Midpoint(self.f, self.b, self.a),
    #         NotCollinear(self.a, self.b, self.c),
    #         Collinear(self.o, self.a, self.d),
    #         Collinear(self.o, self.b, self.e),
    #         Collinear(self.o, self.c, self.f),
    #         Between(self.o, self.a, self.d),
    #         Between(self.o, self.b, self.e),
    #         Between(self.o, self.c, self.f),
    #     ]


class IsIncenterOf(Relation):
    def __init__(self, o: Point, p1: Point, p2: Point, p3: Point):
        super().__init__()
        self.o = o
        self.p1, self.p2, self.p3 = sort_points(p1, p2, p3)
    
    def permutations(self):
        return [(self.o, *perm) for perm in itertools.permutations([self.p1, self.p2, self.p3])]

    # def definition(self):
    #     return [
    #         Angle(self.p3, self.p2, self.p1) - Angle(self.p1, self.p2, self.p4),
    #         Angle(self.p2, self.p4, self.p1) - Angle(self.p1, self.p4, self.p3),
    #         Angle(self.p4, self.p3, self.p1) - Angle(self.p1, self.p3, self.p2),
    #     ]


class IsRadiusOf(Relation):
    def __init__(self, a: Point, b: Point, o: Point):
        super().__init__()
        self.a, self.b = sort_points(a, b)
        self.o = o
    
    def permutations(self):
        return [(self.a, self.b, self.o), (self.b, self.a, self.o)]
    
    
class IsDiameterOf(Relation):
    def __init__(self, a: Point, b: Point, o: Point):
        super().__init__()
        self.a, self.b = sort_points(a, b)
        self.o = o
    
    def permutations(self):
        return [(self.a, self.b, self.o), (self.b, self.a, self.o)]
    

class IsMidsegmentOf(Relation):
    def __init__(self, a: Point, b: Point, p1: Point, p2: Point, p3: Point):
        super().__init__()
        self.a, self.b = sort_points(a, b)
        self.p1, self.p2, self.p3 = sort_points(p1, p2, p3)
    
    def permutations(self):
        triangle_perms = itertools.permutations([self.p1, self.p2, self.p3])
        return [
            (x, y, *perm)
            for x, y in [(self.a, self.b), (self.b, self.a)]
            for perm in triangle_perms
        ]
        
class IsChordOf(Relation):
    def __init__(self, a: Point, b: Point, o: Point):
        super().__init__()
        self.a, self.b = sort_points(a, b)
        self.o = o
    
    def permutations(self):
        return [(self.a, self.b, self.o), (self.b, self.a, self.o)]


class IsHypotenuseOf(Relation):
    def __init__(self, a: Point, b: Point, p1: Point, p2: Point, p3: Point):
        super().__init__()
        self.a, self.b = sort_points(a, b)
        self.p1, self.p2, self.p3 = sort_points(p1, p2, p3)
    
    def permutations(self):
        triangle_perms = itertools.permutations([self.p1, self.p2, self.p3])
        return [
            (x, y, *perm)
            for x, y in [(self.a, self.b), (self.b, self.a)]
            for perm in triangle_perms
        ]


class IsPerpendicularBisectorOf(Relation):
    def __init__(self, a: Point, b: Point, p1: Point, p2: Point, p3: Point):
        super().__init__()
        self.a, self.b = sort_points(a, b)
        self.p1, self.p2, self.p3 = sort_points(p1, p2, p3)
    
    def permutations(self):
        triangle_perms = itertools.permutations([self.p1, self.p2, self.p3])
        return [
            (x, y, *perm)
            for x, y in [(self.a, self.b), (self.b, self.a)]
            for perm in triangle_perms
        ]


class IsAltitudeOf(Relation):
    def __init__(self, a: Point, b: Point, p1: Point, p2: Point, p3: Point):
        super().__init__()
        self.a, self.b = sort_points(a, b)
        self.p1, self.p2, self.p3 = sort_points(p1, p2, p3)
    
    def permutations(self):
        triangle_perms = itertools.permutations([self.p1, self.p2, self.p3])
        return [
            (x, y, *perm)
            for x, y in [(self.a, self.b), (self.b, self.a)]
            for perm in triangle_perms
        ]


class IsMedianOf(Relation):
    def __init__(self, a: Point, b: Point, p1: Point, p2: Point, p3: Point):
        super().__init__()
        self.a, self.b = sort_points(a, b)
        self.p1, self.p2, self.p3 = sort_points(p1, p2, p3)
    
    def permutations(self):
        triangle_perms = itertools.permutations([self.p1, self.p2, self.p3])
        return [
            (x, y, *perm)
            for x, y in [(self.a, self.b), (self.b, self.a)]
            for perm in triangle_perms
        ]


def AreaOf(obj: Object):
    object_name = obj.__class__.__name__
    ps = obj.get_points()
    if not isinstance(obj) or len(ps) < 3:
        raise UnsupportedRelation(f"Area expects a geometric object with at least 3 points, but got {type(obj).__name__}")
    return Symbol("_".join([f"AreaOf{object_name}"] + [str(item) for item in ps]), positive=True)


def PerimeterOf(obj: Object):
    object_name = obj.__class__.__name__
    ps = obj.get_points()
    if not isinstance(obj) or len(ps) < 3:
        raise UnsupportedRelation(f"Perimeter expects a geometric object with at least 3 points, but got {type(obj).__name__}")
    return Symbol("_".join([f"PerimeterOf{object_name}"] + [str(item) for item in ps]), positive=True)


def Radius(o: Point):
    return Symbol(f"RadiusOfCircle_{str(o)}", positive=True)


def RadiusOf(obj: Object):
    if not isinstance(obj, Circle):
        raise UnsupportedRelation(f"Radius expects a Circle, but got {type(obj).__name__}")
    
    return Symbol(f"RadiusOfCircle_{str(obj.o)}", positive=True)


def DiameterOf(obj: Object):
    if not isinstance(obj, Circle):
        raise UnsupportedRelation(f"Diameter expects a Circle, but got {type(obj).__name__}")
    
    return Symbol(f"DiameterOfCircle_{str(obj.o)}", positive=True)


def CircumferenceOf(obj: Object):
    if not isinstance(obj, Circle):
        raise UnsupportedRelation(f"Circumference expects a Circle, but got {type(obj).__name__}")
    
    return Symbol(f"CircumferenceOfCircle_{str(obj.o)}", positive=True)


def Radian(p1: Point, p2: Point, p3: Point):
    p1, p3 = sort_points(p1, p3)
    return Symbol(f"RadianOfAngle_{str(p1)}_{str(p2)}_{str(p3)}", non_negative=True)


def RadianOf(obj: Object):
    if not isinstance(obj, Angle):
        raise UnsupportedRelation(f"Radian expects an Angle, but got {type(obj).__name__}")
    
    return Symbol(f"RadianOfAngle_{str(obj.a)}_{str(obj.b)}_{str(obj.c)}", non_negative=True)


def DegreeOf(obj: Object):
    if not isinstance(obj, Angle):
        raise UnsupportedRelation(f"Degree expects an Angle, but got {type(obj).__name__}")
    
    return (Symbol(f"RadianOfAngle_{str(obj.a)}_{str(obj.b)}_{str(obj.c)}", non_negative=True) / pi) * 180


def Length(p1: Point, p2: Point):
    p1, p2 = sort_points(p1, p2)
    return Symbol(f"LengthOfSegment_{str(p1)}_{str(p2)}", positive=True)


def LengthOf(obj: Object):
    if isinstance(obj, Segment):
        return Symbol(f"LengthOfSegment_{str(obj.a)}_{str(obj.b)}", positive=True)
    elif isinstance(obj, Arc):
        return Symbol(f"LengthOfArc_{str(obj.a)}_{str(obj.o)}_{str(obj.b)}", positive=True)
    else:
        raise UnsupportedRelation(f"Length expects a Segment or Arc, but got {type(obj).__name__}")


def SideOf(obj: Object):
    object_name = obj.__class__.__name__
    ps = obj.get_points()
    if not isinstance(obj) or len(ps) < 3:
        raise UnsupportedRelation(f"Side expects a geometric object with at least 3 points, but got {type(obj).__name__}")
    
    return Symbol("_".join([f"SideOf{object_name}"] + [str(item) for item in ps]), positive=True)


def ScaleFactorOf(obj1: Object, obj2: Object):
    if not type(obj1) == type(obj2):
        raise UnsupportedRelation(f"ScaleFactor expects two same geometric objects, but got {type(obj1).__name__} and {type(obj2).__name__}")
    
    object_name = obj1.__class__.__name__
    ps1 = obj1.get_points()
    ps2 = obj2.get_points()
    str1 = "_".join([object_name] + [str(item) for item in ps1])
    str2 = "_".join([object_name] + [str(item) for item in ps2])
    return Symbol(f"ScaleFactorOf_{str1}_{str2}", positive=True)


def Variable(name: str):
    return Symbol(f"Variable_{name}")


# def get_points_and_symbols(eqn):
#     pattern = re.compile(r"((?:Angle|Length|Area|Variable)\w+)")
#     # eqn.free_symbols is not apRelationoriate in this case, we need an ordered list instead of a set
#     matches = pattern.findall(str(eqn))
#     symbols = []
#     points = []
#     for match in matches:
#         cls, args = match.split("_")[0], match.split("_")[1:]
#         if cls == "Variable":
#             arg = "_".join(match.split("_")[1:])
#             symbol = Variable(arg)
#         else:
#             args = [Point(item) for item in args]
#             if cls == "Angle":
#                 symbol = Angle(*args)
#             elif cls == "Length":
#                 symbol = Length(*args)
#             elif cls == "Area":
#                 symbol = Area(*args)
#             points += args
#         symbols.append(symbol)
#     return points, symbols
