from __future__ import annotations

import copy
import re
import itertools

from sympy import Symbol, pi
from pyeuclid.formalization.utils import sort_points, sort_cyclic_points, sort_point_groups


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

    def negate(self):
        self.negated = not self.negated
        
    def get_points(self):
        points = []
        for v in vars(self).values():
            if isinstance(v, Point):
                points.append(v)
            elif isinstance(v, list):
                for p in v:
                    if isinstance(p, Point):
                        points.append(p)
        return points

    def __str__(self):
        class_name = self.__class__.__name__
        points = self.get_points()
        args_name = ",".join([p.name for p in points])
        
        if not self.negated:
            return f"{class_name}({args_name})"
        else:
            return f"Not({class_name}({args_name}))"

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return str(self) == str(other)

    def __hash__(self):
        return hash(str(self))


class Lt(Relation):
    def __init__(self, v1: Point, v2: Point):
        """
        Used for obtaining a canonical order of assignments
        """
        super().__init__()
        self.v1 = v1
        self.v2 = v2


class Equal(Relation):
    def __init__(self, v1: Point, v2: Point):
        super().__init__()
        self.v1, self.v2 = sort_points(v1, v2)

    def permutations(self):
        return [(self.v1, self.v2), (self.v2, self.v1)]


def Not(p: Relation) -> Relation:
    other = copy.copy(p)
    other.negate()
    return other


def Angle(p1: Point, p2: Point, p3: Point):
    p1, p3 = sort_points(p1, p3)
    return Symbol(f"Angle_{p1}_{p2}_{p3}", non_negative=True)


def Length(p1: Point, p2: Point):
    p1, p2 = sort_points(p1, p2)
    return Symbol(f"Length_{str(p1)}_{str(p2)}", positive=True)


def Area(*ps: list[Point]):
    ps = sort_points(*ps)
    return Symbol("_".join(["Area"] + [str(item) for item in ps]), positive=True)


def Variable(name: str):
    return Symbol(f"Variable_{name}")


class Different(Relation):
    def __init__(self, *ps: list[Point]):
        super().__init__()
        self.ps = ps

    def definition(self):
        return [Not(Equal(self.ps[i], self.ps[j])) for i in range(len(self.ps)) for j in range(i + 1, len(self.ps))]


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
            (self.p1, self.p2, self.p4, self.p3),
            (self.p2, self.p1, self.p3, self.p4),
            (self.p2, self.p1, self.p4, self.p3),
        ]


class OppositeSide(Relation):
    def __init__(self, p1: Point, p2: Point, p3: Point, p4: Point):
        super().__init__()
        self.p1, self.p2 = sort_points(p1, p2)
        self.p3, self.p4 = sort_points(p3, p4)

    def definition(self):
        return [
            Not(Collinear(self.p1, self.p3, self.p4)),
            Not(Collinear(self.p2, self.p3, self.p4)),
            Not(SameSide(self.p1, self.p2, self.p3, self.p4)),
        ]


class Collinear(Relation):
    def __init__(self, p1, p2, p3):
        super().__init__()
        self.p1, self.p2, self.p3 = sort_points(p1, p2, p3)

    def permutations(self):
        return itertools.permutations([self.p1, self.p2, self.p3])


class NotCollinear(Relation):
    def __init__(self, p1, p2, p3):
        super().__init__()
        self.p1, self.p2, self.p3 = sort_points(p1, p2, p3)

    def definition(self):
        return [
            Not(Collinear(self.p1, self.p2, self.p3)),
            Different(self.p1, self.p2, self.p3)
        ]


class Midpoint(Relation):
    def __init__(self, p1: Point, p2: Point, p3: Point):
        super().__init__()
        self.p1 = p1
        self.p2, self.p3 = sort_points(p2, p3)

    def definition(self):
        return [
            Length(self.p1, self.p2) - Length(self.p1, self.p3),
            Collinear(self.p1, self.p2, self.p3),
            Different(self.p2, self.p3),
            Between(self.p1, self.p2, self.p3),
        ]
        

class Congruent(Relation):
    def __init__(
        self, p1: Point, p2: Point, p3: Point, p4: Point, p5: Point, p6: Point
    ):
        super().__init__()
        self.p1, self.p2, self.p3, self.p4, self.p5, self.p6 = p1, p2, p3, p4, p5, p6

    def definition(self):
        return [
            Length(self.p1, self.p2) - Length(self.p4, self.p5),
            Length(self.p2, self.p3) - Length(self.p5, self.p6),
            Length(self.p1, self.p3) - Length(self.p4, self.p6),
            NotCollinear(self.p1, self.p2, self.p3),
        ]


class Similar(Relation):
    def __init__(
        self, p1: Point, p2: Point, p3: Point, p4: Point, p5: Point, p6: Point
    ):
        super().__init__()
        self.p1, self.p2, self.p3, self.p4, self.p5, self.p6 = p1, p2, p3, p4, p5, p6

    def definition(self):
        return [
            Length(self.p1, self.p2) / Length(self.p4, self.p5)
            - Length(self.p2, self.p3) / Length(self.p5, self.p6),
            Length(self.p1, self.p2) / Length(self.p4, self.p5)
            - Length(self.p3, self.p1) / Length(self.p6, self.p4),
            NotCollinear(self.p1, self.p2, self.p3),
        ]


class Concyclic(Relation):
    def __init__(self, *ps: Point):
        super().__init__()
        self.ps = list(sort_points(*ps))

    def permutations(self):
        return itertools.permutations(self.ps)


class Parallel(Relation):
    def __init__(self, p1: Point, p2: Point, p3: Point, p4: Point):
        super().__init__()
        p1, p2 = sort_points(p1, p2)
        p3, p4 = sort_points(p3, p4)
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


class Perpendicular(Relation):
    def __init__(self, p1: Point, p2: Point, p3: Point, p4: Point):
        super().__init__()
        p1, p2 = sort_points(p1, p2)
        p3, p4 = sort_points(p3, p4)
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


class Quadrilateral(Relation):
    def __init__(self, p1: Point, p2: Point, p3: Point, p4: Point):
        super().__init__()
        self.p1, self.p2, self.p3, self.p4 = sort_cyclic_points(p1, p2, p3, p4)

    def permutations(self):
        return [
            (self.p1, self.p2, self.p3, self.p4),
            (self.p2, self.p3, self.p4, self.p1),
            (self.p3, self.p4, self.p1, self.p2),
            (self.p4, self.p1, self.p2, self.p3),
            (self.p4, self.p3, self.p2, self.p1),
            (self.p3, self.p2, self.p1, self.p4),
            (self.p2, self.p1, self.p4, self.p3),
            (self.p1, self.p4, self.p3, self.p2),
        ]

    def definition(self):
        return [
            OppositeSide(self.p1, self.p3, self.p2, self.p4),
            OppositeSide(self.p2, self.p4, self.p1, self.p3),
        ]


class Pentagon(Relation):
    def __init__(self, p1: Point, p2: Point, p3: Point, p4: Point, p5: Point):
        super().__init__()
        self.p1, self.p2, self.p3, self.p4, self.p5 = sort_cyclic_points(p1, p2, p3, p4, p5)

    def permutations(self):
        return [
            (self.p1, self.p2, self.p3, self.p4, self.p5),
            (self.p2, self.p3, self.p4, self.p5, self.p1),
            (self.p3, self.p4, self.p5, self.p1, self.p2),
            (self.p4, self.p5, self.p1, self.p2, self.p3),
            (self.p5, self.p1, self.p2, self.p3, self.p4),
            (self.p5, self.p4, self.p3, self.p2, self.p1),
            (self.p4, self.p3, self.p2, self.p1, self.p5),
            (self.p3, self.p2, self.p1, self.p5, self.p4),
            (self.p2, self.p1, self.p5, self.p4, self.p3),
            (self.p1, self.p5, self.p4, self.p3, self.p2),
        ]


class Similar4P(Relation):
    def __init__(
        self,
        p1: Point,
        p2: Point,
        p3: Point,
        p4: Point,
        p5: Point,
        p6: Point,
        p7: Point,
        p8: Point,
    ):
        super().__init__()
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3
        self.p4 = p4
        self.p5 = p5
        self.p6 = p6
        self.p7 = p7
        self.p8 = p8

    def definition(self):
        return [
            Length(self.p1, self.p2) / Length(self.p5, self.p6)
            - Length(self.p2, self.p3) / Length(self.p6, self.p7),
            Length(self.p1, self.p2) / Length(self.p5, self.p6)
            - Length(self.p3, self.p4) / Length(self.p7, self.p8),
            Length(self.p1, self.p2) / Length(self.p5, self.p6)
            - Length(self.p4, self.p1) / Length(self.p8, self.p5),
            Angle(self.p1, self.p2, self.p3) - Angle(self.p5, self.p6, self.p7),
            Angle(self.p2, self.p3, self.p4) - Angle(self.p6, self.p7, self.p8),
            Angle(self.p3, self.p4, self.p1) - Angle(self.p7, self.p8, self.p5),
            Angle(self.p4, self.p1, self.p2) - Angle(self.p8, self.p5, self.p6),
        ]


class Similar5P(Relation):
    def __init__(
        self,
        p1: Point,
        p2: Point,
        p3: Point,
        p4: Point,
        p5: Point,
        p6: Point,
        p7: Point,
        p8: Point,
        p9: Point,
        p10: Point,
    ):
        super().__init__()
        self.p1, self.p2, self.p3, self.p4, self.p5, self.p6, self.p7, self.p8, self.p9, self.p10 = p1, p2, p3, p4, p5, p6, p7, p8, p9, p10

    def definition(self):
        return [
            Length(self.p1, self.p2) / Length(self.p6, self.p7)
            - Length(self.p2, self.p3) / Length(self.p7, self.p8),
            Length(self.p2, self.p3) / Length(self.p7, self.p8)
            - Length(self.p3, self.p4) / Length(self.p8, self.p9),
            Length(self.p3, self.p4) / Length(self.p8, self.p9)
            - Length(self.p4, self.p5) / Length(self.p9, self.p10),
            Length(self.p4, self.p5) / Length(self.p9, self.p10)
            - Length(self.p5, self.p1) / Length(self.p10, self.p6),
            Length(self.p5, self.p1) / Length(self.p10, self.p6)
            - Length(self.p1, self.p2) / Length(self.p6, self.p7),
            Angle(self.p1, self.p2, self.p3) - Angle(self.p6, self.p7, self.p8),
            Angle(self.p2, self.p3, self.p4) - Angle(self.p7, self.p8, self.p9),
            Angle(self.p3, self.p4, self.p5) - Angle(self.p8, self.p9, self.p10),
            Angle(self.p4, self.p5, self.p1) - Angle(self.p9, self.p10, self.p6),
            Angle(self.p5, self.p1, self.p2) - Angle(self.p10, self.p6, self.p7),
        ]


class Parallelogram(Relation):
    def __init__(self, p1: Point, p2: Point, p3: Point, p4: Point):
        super().__init__()
        self.p1, self.p2, self.p3, self.p4 = sort_cyclic_points(p1, p2, p3, p4)

    def definition(self):
        return [
            Parallel(self.p1, self.p2, self.p3, self.p4),
            Parallel(self.p2, self.p3, self.p4, self.p1),
            Quadrilateral(self.p1, self.p2, self.p3, self.p4),
        ]


class Square(Relation):
    def __init__(self, p1: Point, p2: Point, p3: Point, p4: Point):
        super().__init__()
        self.p1, self.p2, self.p3, self.p4 = sort_cyclic_points(p1, p2, p3, p4)

    def definition(self):
        return [
            Length(self.p1, self.p2) - Length(self.p2, self.p3),
            Length(self.p2, self.p3) - Length(self.p3, self.p4),
            Length(self.p3, self.p4) - Length(self.p4, self.p1),
            Length(self.p4, self.p1) - Length(self.p1, self.p2),
            Angle(self.p1, self.p2, self.p3) - pi / 2,
            Angle(self.p2, self.p3, self.p4) - pi / 2,
            Angle(self.p3, self.p4, self.p1) - pi / 2,
            Angle(self.p4, self.p1, self.p2) - pi / 2,
            Quadrilateral(self.p1, self.p2, self.p3, self.p4),
        ]


class Rectangle(Relation):
    def __init__(self, p1: Point, p2: Point, p3: Point, p4: Point):
        super().__init__()
        self.p1, self.p2, self.p3, self.p4 = sort_cyclic_points(p1, p2, p3, p4)

    def definition(self):
        return [
            Length(self.p1, self.p2) - Length(self.p3, self.p4),
            Length(self.p2, self.p3) - Length(self.p4, self.p1),
            Angle(self.p1, self.p2, self.p3) - pi / 2,
            Angle(self.p2, self.p3, self.p4) - pi / 2,
            Angle(self.p3, self.p4, self.p1) - pi / 2,
            Angle(self.p4, self.p1, self.p2) - pi / 2,
            Quadrilateral(self.p1, self.p2, self.p3, self.p4),
        ]


class Rhombus(Relation):
    def __init__(self, p1: Point, p2: Point, p3: Point, p4: Point):
        super().__init__()
        self.p1, self.p2, self.p3, self.p4 = sort_cyclic_points(p1, p2, p3, p4)

    def definition(self):
        return [
            Length(self.p1, self.p2) - Length(self.p2, self.p3),
            Length(self.p2, self.p3) - Length(self.p3, self.p4),
            Length(self.p3, self.p4) - Length(self.p4, self.p1),
            Length(self.p4, self.p1) - Length(self.p1, self.p2),
            Perpendicular(self.p1, self.p3, self.p2, self.p4),
            Quadrilateral(self.p1, self.p2, self.p3, self.p4),
        ]


class Trapezoid(Relation):
    def __init__(self, p1: Point, p2: Point, p3: Point, p4: Point):
        super().__init__()
        if p1.name > p3.name:
            if p3.name > p4.name:
                self.p1, self.p2, self.p3, self.p4 = p4, p3, p2, p1
            else:
                self.p1, self.p2, self.p3, self.p4 = p3, p4, p1, p2
        else:
            if p1.name > p2.name:
                self.p1, self.p2, self.p3, self.p4 = p2, p1, p4, p3
            else:
                self.p1, self.p2, self.p3, self.p4 = p1, p2, p3, p4

    def definition(self):
        return [
            Parallel(self.p1, self.p2, self.p3, self.p4),
            Quadrilateral(self.p1, self.p2, self.p3, self.p4),
        ]


class Kite(Relation):
    def __init__(self, p1: Point, p2: Point, p3: Point, p4: Point):
        super().__init__()
        self.p1, self.p2, self.p3, self.p4 = p1, p2, p3, p4

    def definition(self):
        return [
            Length(self.p1, self.p2) - Length(self.p2, self.p3),
            Length(self.p3, self.p4) - Length(self.p4, self.p1),
            Angle(self.p2, self.p1, self.p4) - Angle(self.p2, self.p3, self.p4),
            Angle(self.p1, self.p2, self.p3) - Angle(self.p1, self.p4, self.p3),
            Different(self.p1, self.p2, self.p3, self.p4),
            Perpendicular(self.p1, self.p3, self.p2, self.p4),
            Quadrilateral(self.p1, self.p2, self.p3, self.p4),
        ]


class Incenter(Relation):
    def __init__(self, p1: Point, p2: Point, p3: Point, p4: Point):
        super().__init__()
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3
        self.p4 = p4

    def definition(self):
        return [
            Angle(self.p3, self.p2, self.p1) - Angle(self.p1, self.p2, self.p4),
            Angle(self.p2, self.p4, self.p1) - Angle(self.p1, self.p4, self.p3),
            Angle(self.p4, self.p3, self.p1) - Angle(self.p1, self.p3, self.p2),
        ]


class Centroid(Relation):
    def __init__(
        self, o: Point, a: Point, b: Point, c: Point, d: Point, e: Point, f: Point
    ):
        super().__init__()
        self.o = o
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        self.e = e
        self.f = f

    def definition(self):
        return [
            Midpoint(self.d, self.b, self.c),
            Midpoint(self.e, self.a, self.c),
            Midpoint(self.f, self.b, self.a),
            NotCollinear(self.a, self.b, self.c),
            Collinear(self.o, self.a, self.d),
            Collinear(self.o, self.b, self.e),
            Collinear(self.o, self.c, self.f),
            Between(self.o, self.a, self.d),
            Between(self.o, self.b, self.e),
            Between(self.o, self.c, self.f),
        ]


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
            points += args
        symbols.append(symbol)
    return points, symbols
