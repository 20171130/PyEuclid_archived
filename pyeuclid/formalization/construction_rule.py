from pyeuclid.formalization.relation import *
from pyeuclid.formalization.utils import *
from sympy import pi

construction_rule_sets = {}


class ConstructionRule:
    def __init__(self, cond_points, new_points):
        self.cond_points = cond_points
        self.new_points = new_points

    def conditions(self):
        return []
    
    def conclusions(self):
        return

    def __str__(self):
        class_name = self.__class__.__name__
        attributes = ",".join(str(value) for _, value in vars(self).items())
        return f"{class_name}({attributes})"


class register:
    def __init__(self, *annotations):
        self.annotations = annotations

    def __call__(self, cls):
        for item in self.annotations:
            if not item in construction_rule_sets:
                construction_rule_sets[item] = [cls]
            else:
                construction_rule_sets[item].append(cls)

        def expanded_conditions(self):
            return expand(self._conditions())

        cls._conditions = cls.conditions
        cls.conditions = expanded_conditions
        return cls


@register("AG")
class construct_angle_bisector(ConstructionRule):
    def __init__(self, cond_points, new_points):
        assert len(cond_points) == 3 and len(new_points) == 1
        self.a, self.b, self.c = cond_points[0], cond_points[1], cond_points[2]
        self.x = new_points[0]

    def conditions(self):
        return [NotCollinear(self.a, self.b, self.c)]

    def conclusions(self):
        return [Angle(self.a, self.b, self.x) - Angle(self.x, self.b, self.c)]


@register("AG")
class construct_angle_mirror(ConstructionRule):
    def __init__(self, cond_points, new_points):
        assert len(cond_points) == 3 and len(new_points) == 1
        self.a, self.b, self.c = cond_points[0], cond_points[1], cond_points[2]
        self.x = new_points[0]

    def conditions(self):
        return [NotCollinear(self.a, self.b, self.c)]

    def conclusions(self):
        return [Angle(self.a, self.b, self.c) - Angle(self.c, self.b, self.x)]


@register("AG")
class construct_circle(ConstructionRule):
    def __init__(self, cond_points, new_points):
        assert len(cond_points) == 3 and len(new_points) == 1
        self.a, self.b, self.c = cond_points[0], cond_points[1], cond_points[2]
        self.x = new_points[0]

    def conditions(self):
        return [NotCollinear(self.a, self.b, self.c)]

    def conclusions(self):
        return [
            Length(self.x, self.a) - Length(self.x, self.b),
            Length(self.x, self.b) - Length(self.x, self.c),
        ]


@register("AG")
class construct_circumcenter(ConstructionRule):
    def __init__(self, cond_points, new_points):
        assert len(cond_points) == 3 and len(new_points) == 1
        self.a, self.b, self.c = cond_points[0], cond_points[1], cond_points[2]
        self.x = new_points[0]

    def conditions(self):
        return [NotCollinear(self.a, self.b, self.c)]

    def conclusions(self):
        return [
            Length(self.x, self.a) - Length(self.x, self.b),
            Length(self.x, self.b) - Length(self.x, self.c),
        ]


# @register("AG")
# class construct_eq_quadrangle(ConstructionRule):
#     def construct(self, x1: Point, x2: Point, x3: Point, x4: Point):
#         return [Length(x1, x4) - Length(x2, x3)]


# @register("AG")
# class construct_eq_trapezoid(ConstructionRule):
#     def construct(self, x1: Point, x2: Point, x3: Point, x4: Point):
#         return [
#             Length(x4, x1) - Length(x2, x3),
#             Parallel(x4, x3, x1, x2),
#             Angle(x4, x1, x2) - Angle(x1, x2, x3),
#             Angle(x2, x3, x4) - Angle(x3, x4, x1),
#         ]


@register("AG")
class construct_eq_triangle(ConstructionRule):
    def __init__(self, cond_points, new_points):
        assert len(cond_points) == 2 and len(new_points) == 1
        self.b, self.c = cond_points[0], cond_points[1]
        self.x = new_points[0]

    def conditions(self):
        return [Different2(self.b, self.c)]

    def conclusions(self):
        return [
            Length(self.x, self.b) - Length(self.b, self.c),
            Length(self.b, self.c) - Length(self.c, self.x),
            Angle(self.x, self.b, self.c) - Angle(self.b, self.c, self.x),
            Angle(self.c, self.x, self.b) - Angle(self.x, self.b, self.c),
        ]


@register("AG")
class construct_eqangle2(ConstructionRule):
    def __init__(self, cond_points, new_points):
        assert len(cond_points) == 3 and len(new_points) == 1
        self.a, self.b, self.c = cond_points[0], cond_points[1], cond_points[2]
        self.x = new_points[0]

    def conditions(self):
        return [NotCollinear(self.a, self.b, self.c)]

    def conclusions(self):
        return [Angle(self.b, self.a, self.x) - Angle(self.x, self.c, self.b)]


# @register("AG")
# class construct_eqdia_quadrangle(ConstructionRule):
#     def construct(self, a: Point, b: Point, c: Point, d: Point):
#         return [Length(d, b) - Length(a, c)]


@register("AG")
class construct_eqdistance(ConstructionRule):
    def __init__(self, cond_points, new_points):
        assert len(cond_points) == 3 and len(new_points) == 1
        self.a, self.b, self.c = cond_points[0], cond_points[1], cond_points[2]
        self.x = new_points[0]

    def conditions(self):
        return [Different2(self.b, self.c)]

    def conclusions(self):
        return [Length(self.x, self.a) - Length(self.b, self.c)]


@register("AG")
class construct_foot(ConstructionRule):
    def __init__(self, cond_points, new_points):
        assert len(cond_points) == 3 and len(new_points) == 1
        self.a, self.b, self.c = cond_points[0], cond_points[1], cond_points[2]
        self.x = new_points[0]

    def conditions(self):
        return [NotCollinear(self.a, self.b, self.c)]

    def conclusions(self):
        return [Perpendicular(self.x, self.a, self.b, self.c), Collinear(self.x, self.b, self.c)]


@register("AG")
class construct_free(ConstructionRule):
    def __init__(self, cond_points, new_points):
        assert len(cond_points) == 0 and len(new_points) == 1
        self.x = new_points[0]


@register("AG")
class construct_incenter(ConstructionRule):
    def __init__(self, cond_points, new_points):
        assert len(cond_points) == 3 and len(new_points) == 1
        self.a, self.b, self.c = cond_points[0], cond_points[1], cond_points[2]
        self.x = new_points[0]

    def conditions(self):
        return [NotCollinear(self.a, self.b, self.c)]

    def conclusions(self):
        return [
            Angle(self.b, self.a, self.x) - Angle(self.x, self.a, self.c),
            Angle(self.a, self.c, self.x) - Angle(self.x, self.c, self.b),
            Angle(self.c, self.b, self.x) - Angle(self.x, self.b, self.a),
        ]


class construct_incenter2(ConstructionRule):
    def __init__(self, cond_points, new_points):
        assert len(cond_points) == 3 and len(new_points) == 4
        self.a, self.b, self.c = cond_points[0], cond_points[1], cond_points[2]
        self.x, self.y, self.z, self.i = new_points[0], new_points[1], new_points[2], new_points[3]

    def conditions(self):
        return [NotCollinear(self.a, self.b, self.c)]

    def conclusions(self):
        return [
            Angle(self.b, self.a, self.i) - Angle(self.i, self.a, self.c),
            Angle(self.a, self.c, self.i) - Angle(self.i, self.c, self.b),
            Angle(self.c, self.b, self.i) - Angle(self.i, self.b, self.a),
            Collinear(self.x, self.b, self.c),
            Perpendicular(self.i, self.x, self.b, self.c),
            Collinear(self.y, self.c, self.a),
            Perpendicular(self.i, self.y, self.c, self.a),
            Collinear(self.z, self.a, self.b),
            Perpendicular(self.i, self.z, self.a, self.b),
            Length(self.i, self.x) - Length(self.i, self.y),
            Length(self.i, self.y) - Length(self.i, self.z),
        ]


@register("AG")
class construct_excenter(ConstructionRule):
    def __init__(self, cond_points, new_points):
        assert len(cond_points) == 3 and len(new_points) == 1
        self.a, self.b, self.c = cond_points[0], cond_points[1], cond_points[2]
        self.x = new_points[0]

    def conditions(self):
        return [NotCollinear(self.a, self.b, self.c)]

    def conclusions(self):
        return [
            Angle(self.b, self.a, self.x) - Angle(self.x, self.a, self.c),
            Angle(self.a, self.b, self.x) - (Angle(self.a, self.b, self.c) / 2 + pi / 2),
            Angle(self.a, self.c, self.x) - (Angle(self.a, self.c, self.b) / 2 + pi / 2),
        ]


class construct_excenter2(ConstructionRule):
    def __init__(self, cond_points, new_points):
        assert len(cond_points) == 3 and len(new_points) == 4
        self.a, self.b, self.c = cond_points[0], cond_points[1], cond_points[2]
        self.x, self.y, self.z, self.i = new_points[0], new_points[1], new_points[2], new_points[3]

    def conditions(self):
        return [NotCollinear(self.a, self.b, self.c)]

    def conclusions(self):
        return [
            Angle(self.b, self.a, self.i) - Angle(self.i, self.a, self.c),
            Angle(self.a, self.b, self.i) - (Angle(self.a, self.b, self.c) / 2 + pi / 2),
            Angle(self.a, self.c, self.i) - (Angle(self.a, self.c, self.b) / 2 + pi / 2),
            Collinear(self.x, self.b, self.c),
            Perpendicular(self.i, self.x, self.b, self.c),
            Collinear(self.y, self.c, self.a),
            Perpendicular(self.i, self.y, self.c, self.a),
            Collinear(self.z, self.a, self.b),
            Perpendicular(self.i, self.z, self.a, self.b),
            Length(self.i, self.x) - Length(self.i, self.y),
            Length(self.i, self.y) - Length(self.i, self.z),
        ]


@register("AG")
class construct_centroid(ConstructionRule):
    def __init__(self, cond_points, new_points):
        assert len(cond_points) == 3 and len(new_points) == 4
        self.a, self.b, self.c = cond_points[0], cond_points[1], cond_points[2]
        self.x, self.y, self.z, self.i = new_points[0], new_points[1], new_points[2], new_points[3]

    def conditions(self):
        return [NotCollinear(self.a, self.b, self.c)]

    def conclusions(self):
        return [
            Collinear(self.x, self.b, self.c),
            Length(self.x, self.b) - Length(self.x, self.c),
            Collinear(self.y, self.c, self.a),
            Length(self.y, self.c) - Length(self.y, self.a),
            Collinear(self.z, self.a, self.b),
            Length(self.z, self.a) - Length(self.z, self.b),
            Collinear(self.a, self.x, self.i),
            Collinear(self.b, self.y, self.i),
            Collinear(self.c, self.z, self.i),
        ]


@register("AG")
class construct_intersection_cc(ConstructionRule):
    def __init__(self, cond_points, new_points):
        assert len(cond_points) == 3 and len(new_points) == 1
        self.o, self.w, self.a = cond_points[0], cond_points[1], cond_points[2]
        self.x = new_points[0]

    def conditions(self):
        return [NotCollinear(self.o, self.w, self.a)]

    def conclusions(self):
        return [
            Length(self.o, self.a) - Length(self.o, self.x),
            Length(self.w, self.a) - Length(self.w, self.x),
        ]


@register("AG")
class construct_intersection_lc(ConstructionRule):
    def __init__(self, cond_points, new_points):
        assert len(cond_points) == 3 and len(new_points) == 1
        self.a, self.o, self.b = cond_points[0], cond_points[1], cond_points[2]
        self.x = new_points[0]

    def conditions(self):
        return [
            Different2(self.a, self.b),
            Different2(self.o, self.b),
            Not(Perpendicular(self.b, self.o, self.b, self.a)),
        ]

    def conclusions(self):
        return [
            Collinear(self.x, self.a, self.b),
            Length(self.o, self.b) - Length(self.o, self.x),
        ]


@register("AG")
class construct_intersection_ll(ConstructionRule):
    def __init__(self, cond_points, new_points):
        assert len(cond_points) == 4 and len(new_points) == 1
        self.a, self.b, self.c, self.d = cond_points[0], cond_points[1], cond_points[2], cond_points[3]
        self.x = new_points[0]

    def conditions(self):
        return [
            Not(Parallel(self.a, self.b, self.c, self.d))
            # ,Not(Collinear(self.a,self.b,self.c,self.d)) # TODO
        ]

    def conclusions(self):
        return [Collinear(self.x, self.a, self.b), Collinear(self.x, self.c, self.d)]


@register("AG")
class construct_intersection_lp(ConstructionRule):
    def __init__(self, cond_points, new_points):
        assert len(cond_points) == 5 and len(new_points) == 1
        self.a, self.b, self.c, self.m, self.n = cond_points[0], cond_points[1], cond_points[2], cond_points[3], cond_points[4]
        self.x = new_points[0]

    def conditions(self):
        return [
            Not(Parallel(self.m, self.n, self.a, self.b)),
            NotCollinear(self.a, self.b, self.c),
            NotCollinear(self.c, self.m, self.n),
        ]

    def conclusions(self):
        return [Collinear(self.x, self.a, self.b), Parallel(self.c, self.x, self.m, self.n)]


@register("AG")
class construct_intersection_lt(ConstructionRule):
    def __init__(self, cond_points, new_points):
        assert len(cond_points) == 5 and len(new_points) == 1
        self.a, self.b, self.c, self.d, self.e = cond_points[0], cond_points[1], cond_points[2], cond_points[3], cond_points[4]
        self.x = new_points[0]

    def conditions(self):
        return [
            NotCollinear(self.a, self.b, self.c),
            Not(Perpendicular(self.a, self.b, self.d, self.e)),
        ]

    def conclusions(self):
        return [Collinear(self.x, self.a, self.b), Perpendicular(self.x, self.c, self.d, self.e)]


@register("AG")
class construct_intersection_pp(ConstructionRule):
    def __init__(self, cond_points, new_points):
        assert len(cond_points) == 6 and len(new_points) == 1
        self.a, self.b, self.c, self.d, self.e, self.f = cond_points[0], cond_points[1], cond_points[2], cond_points[3], cond_points[4], cond_points[5]
        self.x = new_points[0]

    def conditions(self):
        return [
            Different2(self.a, self.d),
            Not(Parallel(self.b, self.c, self.e, self.f)),
        ]

    def conclusions(self):
        return [
            Parallel(self.x, self.a, self.b, self.c),
            Parallel(self.x, self.d, self.e, self.f),
        ]


@register("AG")
class construct_intersection_tt(ConstructionRule):
    def __init__(self, cond_points, new_points):
        assert len(cond_points) == 6 and len(new_points) == 1
        self.a, self.b, self.c, self.d, self.e, self.f = cond_points[0], cond_points[1], cond_points[2], cond_points[3], cond_points[4], cond_points[5]
        self.x = new_points[0]

    def conditions(self):
        return [
            Different2(self.a, self.d),
            Not(Parallel(self.b, self.c, self.e, self.f)),
        ]

    def conclusions(self):
        return [
            Perpendicular(self.x, self.a, self.b, self.c),
            Perpendicular(self.x, self.d, self.e, self.f),
        ]


@register("AG")
class construct_iso_triangle(ConstructionRule):
    def __init__(self, cond_points, new_points):
        assert len(cond_points) == 0 and len(new_points) == 3
        self.a, self.b, self.c = new_points[0], new_points[1], new_points[2]
        
    def conclusions(self):
        return [Length(self.a, self.b) - Length(self.a, self.c), Angle(self.a, self.b, self.c) - Angle(self.b, self.c, self.a)]


@register("AG")
class construct_lc_tangent(ConstructionRule):
    def __init__(self, cond_points, new_points):
        assert len(cond_points) == 2 and len(new_points) == 1
        self.a, self.o = cond_points[0], cond_points[1]
        self.x = new_points[0]

    def conditions(self):
        return [Different2(self.a, self.o)]

    def conclusions(self):
        return [Perpendicular(self.a, self.x, self.a, self.o)]


@register("AG")
class construct_midpoint(ConstructionRule):
    def __init__(self, cond_points, new_points):
        assert len(cond_points) == 2 and len(new_points) == 1
        self.a, self.b = cond_points[0], cond_points[1]
        self.x = new_points[0]

    def conditions(self):
        return [Different2(self.a, self.b)]

    def conclusions(self):
        return [Collinear(self.x, self.a, self.b), Length(self.x, self.a) - Length(self.x, self.b)]


@register("AG")
class construct_mirror(ConstructionRule):
    def __init__(self, cond_points, new_points):
        assert len(cond_points) == 2 and len(new_points) == 1
        self.a, self.b = cond_points[0], cond_points[1]
        self.x = new_points[0]

    def conditions(self):
        return [Different2(self.a, self.b)]

    def conclusions(self):
        return [
            Length(self.b, self.a) - Length(self.b, self.x),
            Collinear(self.x, self.a, self.b),
        ]


@register("AG")
class construct_nsquare(ConstructionRule):
    def __init__(self, cond_points, new_points):
        assert len(cond_points) == 2 and len(new_points) == 1
        self.a, self.b = cond_points[0], cond_points[1]
        self.x = new_points[0]

    def conditions(self):
        return [Different2(self.a, self.b)]

    def conclusions(self):
        return [
            Length(self.x, self.a) - Length(self.a, self.b),
            Perpendicular(self.x, self.a, self.a, self.b),
        ]


@register("AG")
class construct_on_aline(ConstructionRule):
    def __init__(self, cond_points, new_points):
        assert len(cond_points) == 5 and len(new_points) == 1
        self.a, self.b, self.c, self.d, self.e = cond_points[0], cond_points[1], cond_points[2], cond_points[3], cond_points[4]
        self.x = new_points[0]

    def conditions(self):
        return [
            NotCollinear(self.c, self.d, self.e),
            Different2(self.a, self.b),
            Different2(self.c, self.d),
            Different2(self.c, self.e),
        ]

    def conclusions(self):
        return [Angle(self.x, self.a, self.b) - Angle(self.c, self.d, self.e)]


@register("AG")
class construct_on_aline2(ConstructionRule):
    def __init__(self, cond_points, new_points):
        assert len(cond_points) == 5 and len(new_points) == 1
        self.a, self.b, self.c, self.d, self.e = cond_points[0], cond_points[1], cond_points[2], cond_points[3], cond_points[4]
        self.x = new_points[0]

    def conditions(self):
        return [
            NotCollinear(self.c, self.d, self.e),
            Different2(self.a, self.b),
            Different2(self.c, self.d),
            Different2(self.c, self.e),
        ]

    def conclusions(self):
        return [Angle(self.x, self.a, self.b) + Angle(self.c, self.d, self.e) - pi]


@register("AG")
class construct_on_bline(ConstructionRule):
    def __init__(self, cond_points, new_points):
        assert len(cond_points) == 2 and len(new_points) == 1
        self.a, self.b = cond_points[0], cond_points[1]
        self.x = new_points[0]

    def conditions(self):
        return [Different2(self.a, self.b)]

    def conclusions(self):
        return [
            Length(self.x, self.a) - Length(self.x, self.b),
            Angle(self.x, self.a, self.b) - Angle(self.a, self.b, self.x),
        ]


@register("AG")
class construct_on_circle(ConstructionRule):
    def __init__(self, cond_points, new_points):
        assert len(cond_points) == 2 and len(new_points) == 1
        self.o, self.a = cond_points[0], cond_points[1]
        self.x = new_points[0]

    def conditions(self):
        return [Different2(self.o, self.a)]

    def conclusions(self):
        return [Length(self.o, self.x) - Length(self.o, self.a)]


@register("AG")
class construct_notonline(ConstructionRule):
    def __init__(self, cond_points, new_points):
        assert len(cond_points) == 2 and len(new_points) == 1
        self.a, self.b = cond_points[0], cond_points[1]
        self.x = new_points[0]

    def conditions(self):
        return [Different2(self.a, self.b)]

    def conclusions(self):
        return [NotCollinear(self.x, self.a, self.b)]


@register("AG")
class construct_on_line(ConstructionRule):
    def __init__(self, cond_points, new_points):
        assert len(cond_points) == 2 and len(new_points) == 1
        self.a, self.b = cond_points[0], cond_points[1]
        self.x = new_points[0]

    def conditions(self):
        return [Different2(self.a, self.b)]

    def conclusions(self):
        return [Collinear(self.x, self.a, self.b)]


@register("AG")
class construct_on_pline(ConstructionRule):
    def __init__(self, cond_points, new_points):
        assert len(cond_points) == 3 and len(new_points) == 1
        self.a, self.b, self.c = cond_points[0], cond_points[1], cond_points[2]
        self.x = new_points[0]

    def conditions(self):
        return [Different2(self.b, self.c), NotCollinear(self.a, self.b, self.c)]

    def conclusions(self):
        return [Parallel(self.x, self.a, self.b, self.c)]


@register("AG")
class construct_on_tline(ConstructionRule):
    def __init__(self, cond_points, new_points):
        assert len(cond_points) == 3 and len(new_points) == 1
        self.a, self.b, self.c = cond_points[0], cond_points[1], cond_points[2]
        self.x = new_points[0]

    def conditions(self):
        return [Different2(self.b, self.c)]

    def conclusions(self):
        return [Perpendicular(self.x, self.a, self.b, self.c)]


@register("AG")
class construct_orthocenter(ConstructionRule):
    def __init__(self, cond_points, new_points):
        assert len(cond_points) == 3 and len(new_points) == 1
        self.a, self.b, self.c = cond_points[0], cond_points[1], cond_points[2]
        self.x = new_points[0]

    def conditions(self):
        return [NotCollinear(self.a, self.b, self.c)]

    def conclusions(self):
        return [
            Perpendicular(self.x, self.a, self.b, self.c),
            Perpendicular(self.x, self.b, self.c, self.a),
            Perpendicular(self.x, self.c, self.a, self.b),
        ]


@register("AG")
class construct_parallelogram(ConstructionRule):
    def __init__(self, cond_points, new_points):
        assert len(cond_points) == 3 and len(new_points) == 1
        self.a, self.b, self.c = cond_points[0], cond_points[1], cond_points[2]
        self.x = new_points[0]

    def conditions(self):
        return [NotCollinear(self.a, self.b, self.c)]

    def conclusions(self):
        return [
            Parallel(self.a, self.b, self.c, self.x),
            Parallel(self.a, self.x, self.b, self.c),
            Length(self.a, self.b) - Length(self.c, self.x),
            Length(self.a, self.x) - Length(self.b, self.c),
        ]


# @register("AG")
# class construct_pentagon(ConstructionRule):
#     def construct(self, x1: Point, x2: Point, x3: Point, x4: Point, x5: Point):
#         return []


@register("AG")
class construct_psquare(ConstructionRule):
    def __init__(self, cond_points, new_points):
        assert len(cond_points) == 2 and len(new_points) == 1
        self.a, self.b = cond_points[0], cond_points[1]
        self.x = new_points[0]

    def conditions(self):
        return [Different2(self.a, self.b)]

    def conclusions(self):
        return [
            Length(self.x, self.a) - Length(self.a, self.b),
            Perpendicular(self.x, self.a, self.a, self.b),
        ]


# @register("AG")
# class construct_quadrangle(ConstructionRule):
#     def construct(self, a: Point, b: Point, c: Point, d: Point):
#         return []


# @register("AG")
# class construct_r_trapezoid(ConstructionRule):
#     def construct(self, a: Point, b: Point, c: Point, d: Point):
#         return [Perpendicular(a, b, a, d), Parallel(a, b, c, d)]


# @register("AG")
# class construct_r_triangle(ConstructionRule):
#     def construct(self, x1: Point, x2: Point, x3: Point):
#         return [Perpendicular(x1, x2, x1, x3)]


@register("AG")
class construct_rectangle(ConstructionRule):
    def __init__(self, cond_points, new_points):
        assert len(cond_points) == 0 and len(new_points) == 4
        self.a, self.b, self.c, self.d = new_points[0], new_points[1], new_points[2], new_points[3]
        
    def conclusions(self):
        return [
            Perpendicular(self.a, self.b, self.b, self.c),
            Parallel(self.a, self.b, self.c, self.d),
            Parallel(self.a, self.d, self.b, self.c),
            Perpendicular(self.a, self.b, self.a, self.d),
            Length(self.a, self.b) - Length(self.c, self.d),
            Length(self.a, self.d) - Length(self.b, self.c),
            Length(self.a, self.c) - Length(self.b, self.d),
        ]


@register("AG")
class construct_s_angle(ConstructionRule):
    def __init__(self, cond_points, new_points):
        assert len(cond_points) == 3 and len(new_points) == 1
        self.a, self.b, self.alpha = cond_points[0], cond_points[1], cond_points[2]
        self.x = new_points[0]

    def conditions(self):
        return [Different2(self.a, self.b)]

    def conclusions(self):
        return [Angle(self.a, self.b, self.x) - sympy.simplify(self.alpha)]


@register("AG")
class construct_s_segment(ConstructionRule):
    def __init__(self, cond_points, new_points):
        assert len(cond_points) == 2 and len(new_points) == 1
        self.a, self.alpha = cond_points[0], cond_points[1]
        self.x = new_points[0]

    def conclusions(self):
        return [Length(self.a, self.x) - sympy.simplify(self.alpha)]


@register("AG")
class construct_reflect(ConstructionRule):
    def __init__(self, cond_points, new_points):
        assert len(cond_points) == 3 and len(new_points) == 1
        self.a, self.b, self.c = cond_points[0], cond_points[1], cond_points[2]
        self.x = new_points[0]

    def conditions(self):
        return [Different2(self.b, self.c), NotCollinear(self.a, self.b, self.c)]

    def conclusions(self):
        return [
            Perpendicular(self.b, self.c, self.a, self.x),
            Length(self.a, self.b) - Length(self.b, self.x),
            Length(self.a, self.c) - Length(self.c, self.x),
        ]


# @register("AG")
# class construct_risos(ConstructionRule):
#     def construct(self, a: Point, b: Point, c: Point):
#         return [
#             Angle(a, b, c) - Angle(b, c, a),
#             Perpendicular(a, b, a, c),
#             Length(a, b) - Length(a, c),
#         ]


# @register("AG")
# class construct_segment(ConstructionRule):
#     def construct(self, a: Point, b: Point):
#         return []


@register("AG")
class construct_shift(ConstructionRule):
    def __init__(self, cond_points, new_points):
        assert len(cond_points) == 3 and len(new_points) == 1
        self.b, self.c, self.d = cond_points[0], cond_points[1], cond_points[2]
        self.x = new_points[0]

    def conditions(self):
        return [Different2(self.d, self.b)]

    def conclusions(self):
        return [
            Length(self.x, self.b) - Length(self.c, self.d),
            Length(self.x, self.c) - Length(self.b, self.d),
        ]


class construct_square(ConstructionRule):
    def __init__(self, cond_points, new_points):
        assert len(cond_points) == 2 and len(new_points) == 2
        self.a, self.b = cond_points[0], cond_points[1]
        self.x, self.y = new_points[0], new_points[1]

    def conditions(self):
        return [Different2(self.a, self.b)]

    def conclusions(self):
        return (
            Perpendicular(self.a, self.b, self.b, self.x),
            Length(self.a, self.b) - Length(self.b, self.x),
            Parallel(self.a, self.b, self.x, self.y),
            Parallel(self.a, self.y, self.b, self.x),
            Perpendicular(self.a, self.y, self.y, self.x),
            Length(self.b, self.x) - Length(self.x, self.y),
            Length(self.x, self.y) - Length(self.y, self.a),
            Perpendicular(self.a, self.x, self.b, self.y),
            Length(self.a, self.x) - Length(self.b, self.y),
        )


@register("AG")
class construct_isquare(ConstructionRule):
    def __init__(self, cond_points, new_points):
        assert len(cond_points) == 0 and len(new_points) == 4
        self.a, self.b, self.c, self.d = new_points[0], new_points[1], new_points[2], new_points[3]
    
    def conclusions(self):
        return (
            Perpendicular(self.a, self.b, self.b, self.c),
            Length(self.a, self.b) - Length(self.b, self.c),
            Parallel(self.a, self.b, self.c, self.d),
            Parallel(self.a, self.d, self.b, self.c),
            Perpendicular(self.a, self.d, self.d, self.c),
            Length(self.b, self.c) - Length(self.c, self.d),
            Length(self.c, self.d) - Length(self.d, self.a),
            Perpendicular(self.a, self.c, self.b, self.d),
            Length(self.a, self.c) - Length(self.b, self.d),
        )


# @register("AG")
# class construct_trapezoid(ConstructionRule):
#     def construct(self, a: Point, b: Point, c: Point, d: Point):
#         return [Parallel(a, b, c, d)]


@register("AG")
class construct_triangle(ConstructionRule):
    def __init__(self, cond_points, new_points):
        assert len(cond_points) == 0 and len(new_points) == 3
        self.a, self.b, self.c = new_points[0], new_points[1], new_points[2]
        

# @register("AG")
# class construct_triangle12(ConstructionRule):
#     def construct(self, a: Point, b: Point, c: Point):
#         return [Length(a, b) / Length(a, c) - 1 / 2]


@register("AG")
class construct_2l1c(ConstructionRule):
    def __init__(self, a: Point, b: Point, c: Point, o: Point):
        self.a = a
        self.b = b
        self.c = c
        self.o = o

    def condition(self):
        return [
            Length(self.o, self.a) - Length(self.o, self.b),
            NotCollinear(self.a, self.b, self.c),
        ]

    def construct(self, x: Point, y: Point, z: Point, i: Point):
        return [
            Collinear(x, self.a, self.c),
            Collinear(y, self.b, self.c),
            Length(self.o, self.a) - Length(self.o, z),
            Collinear(i, self.o, z),
            Length(i, x) - Length(i, y),
            Length(i, y) - Length(i, z),
            Perpendicular(i, x, self.a, self.c),
            Perpendicular(i, y, self.b, self.c),
        ]


@register("AG")
class construct_e5128(ConstructionRule):
    def __init__(self, a: Point, b: Point, c: Point, d: Point):
        self.d = d
        self.a = a
        self.b = b
        self.c = c

    def condition(self):
        return [
            Length(self.c, self.b) - Length(self.c, self.d),
            Perpendicular(self.b, self.c, self.b, self.a),
        ]

    def construct(self, x: Point, y: Point):
        return [
            Length(self.c, self.b) - Length(self.c, x),
            Collinear(y, self.a, self.b),
            Collinear(x, y, self.d),
            Angle(self.b, self.a, self.d) - Angle(self.a, x, y),
        ]


@register("AG")
class construct_3peq(ConstructionRule):
    def __init__(self, a: Point, b: Point, c: Point):
        self.a = a
        self.b = b
        self.c = c

    def condition(self):
        return [NotCollinear(self.a, self.b, self.c)]

    def construct(self, x: Point, y: Point, z: Point):
        return [
            Collinear(z, self.b, self.c),
            Collinear(x, self.a, self.b),
            Collinear(y, self.a, self.c),
            Collinear(x, y, z),
            Length(z, x) - Length(z, y),
        ]


@register("AG")
class construct_trisect(ConstructionRule):
    def __init__(self, a: Point, b: Point, c: Point):
        self.a = a
        self.b = b
        self.c = c

    def condition(self):
        return [NotCollinear(self.a, self.b, self.c)]

    def construct(self, x: Point, y: Point):
        return [
            Angle(self.a, self.b, x) - Angle(x, self.b, y),
            Angle(x, self.b, y) - Angle(y, self.b, self.c),
            Collinear(x, self.a, self.c),
            Collinear(y, self.a, self.c),
        ]


@register("AG")
class construct_trisegment(ConstructionRule):
    def __init__(self, a: Point, b: Point):
        self.a = a
        self.b = b

    def condition(self):
        return [Different2(self.a, self.b)]

    def construct(self, x: Point, y: Point):
        return [
            Length(self.a, x) - Length(x, y),
            Length(x, y) - Length(y, self.b),
            Collinear(x, self.a, self.b),
            Collinear(y, self.a, self.b),
        ]


@register("AG")
class construct_on_dia(ConstructionRule):
    def __init__(self, a: Point, b: Point):
        self.a = a
        self.b = b

    def condition(self):
        return [Different2(self.a, self.b)]

    def construct(self, x: Point):
        return [Perpendicular(x, self.a, x, self.b)]


@register("AG")
class construct_ieq_triangle(ConstructionRule):

    def construct(self, a: Point, b: Point, c: Point):
        return [
            Length(a, b) - Length(b, c),
            Length(b, c) - Length(c, a),
            Angle(b, a, c) - Angle(a, c, b),
            Angle(a, c, b) - Angle(c, b, a),
        ]


@register("AG")
class construct_on_opline(ConstructionRule):
    def __init__(self, a: Point, b: Point):
        self.a = a
        self.b = b

    def condition(self):
        return [Different2(self.a, self.b)]

    def construct(self, x: Point):
        return [Collinear(x, self.a, self.b)]


class construct_cc_tangent(ConstructionRule):
    def __init__(self, o: Point, a: Point, w: Point, b: Point):
        self.o = o
        self.a = a
        self.w = w
        self.b = b

    def condition(self):
        return [
            Different2(self.o, self.a),
            Different2(self.w, self.b),
            Different2(self.o, self.w),
        ]

    def construct(self, x: Point, y: Point, z: Point, i: Point):
        return [
            Length(self.o, x) - Length(self.o, self.a),
            Length(self.w, y) - Length(self.w, self.b),
            Perpendicular(x, self.o, x, y),
            Perpendicular(y, self.w, y, x),
            Length(self.o, z) - Length(self.o, self.a),
            Length(self.w, i) - Length(self.w, self.b),
            Perpendicular(z, self.o, z, i),
            Perpendicular(i, self.w, i, z),
        ]


@register("AG")
class construct_eqangle3(ConstructionRule):
    def __init__(self, a: Point, b: Point, d: Point, e: Point, f: Point):
        self.a = a
        self.b = b
        self.d = d
        self.e = e
        self.f = f

    def condition(self):
        return [
            NotCollinear(self.d, self.e, self.f),
            Different2(self.a, self.b),
            Different2(self.d, self.e),
            Different2(self.e, self.f),
        ]

    def construct(self, x: Point):
        return [Angle(self.a, x, self.b) - Angle(self.e, self.d, self.f)]


@register("AG")
class construct_tangent(ConstructionRule):
    def __init__(self, a: Point, o: Point, b: Point):

        self.a = a
        self.o = o
        self.b = b

    def condition(self):
        return [
            Different2(self.o, self.a),
            Different2(self.o, self.b),
            Different2(self.a, self.b),
        ]

    def construct(self, x: Point, y: Point):
        return [
            Length(self.o, x) - Length(self.o, self.b),
            Perpendicular(self.a, x, self.o, x),
            Length(self.o, y) - Length(self.o, self.b),
            Perpendicular(self.a, y, self.o, y),
        ]


class construct_ParallelPostulate1(ConstructionRule):
    def __init__(self, a: Point, b: Point, c: Point, d: Point):
        self.a = a
        self.b = b
        self.c = c
        self.d = d

    def condition(self):
        return [Not(Parallel(self.a, self.b, self.c, self.d))]

    def construct(self, x: Point):
        return [Collinear(self.a, x, self.b), Collinear(self.c, x, self.d)]


class construct_sameside(ConstructionRule):
    def __init__(self, a: Point, b: Point, c: Point):
        self.a = a
        self.b = b
        self.c = c

    def condition(self):
        return [NotCollinear(self.a, self.b, self.c)]

    def construct(self, x: Point):
        return [SameSide(x, self.a, self.b, self.c)]


class construct_oppositeside(ConstructionRule):
    def __init__(self, a: Point, b: Point, c: Point):
        self.a = a
        self.b = b
        self.c = c

    def condition(self):
        return [NotCollinear(self.a, self.b, self.c)]

    def construct(self, x: Point):
        return [OppositeSide(x, self.a, self.b, self.c)]
