import inspect
from sympy import pi

from pyeuclid.formalization.relation import *
from pyeuclid.formalization.utils import *


construction_rule_sets = {}


class ConstructionRule:
    def __init__(self):
        pass
    
    def construct(self):
        pass

    def conditions(self):
        return []
    
    def conclusions(self):
        return []

    def __str__(self):
        class_name = self.__class__.__name__
        inputs = ",".join(str(input) for input in self.inputs)
        if self.outputs:
            outputs = ",".join(str(out) for out in self.outputs)
            return f"{outputs} = {class_name}({inputs})"
        
        return f"{class_name}({inputs})"


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
            return expand_definition(self._conditions())

        cls._conditions = cls.conditions
        cls.conditions = expanded_conditions
        
        init_sig = inspect.signature(cls.__init__)
        init_params = list(init_sig.parameters.values())[1:]
        cls.input_types = [p.annotation for p in init_params]
        cls.num_inputs = len(cls.input_types)
        
        construct_sig = inspect.signature(cls.construct)
        cls.num_outputs = len(construct_sig.parameters) - 1
        
        return cls


@register("nondeterministic")
class construct_angle_bisector(ConstructionRule):
    def __init__(self, a: Point, b: Point, c: Point):
        self.inputs = [a, b, c]
        self.outputs = None
        
    def construct(self, x: Point):
        self.outputs = [x]

    def conditions(self):
        a, b, c = self.inputs
        return [NotCollinear(a, b, c)]

    def conclusions(self):
        a, b, c = self.inputs
        x, = self.outputs
        return [Angle(a, b, x) - Angle(x, b, c)]


@register("nondeterministic")
class construct_angle_mirror(ConstructionRule):
    def __init__(self, a: Point, b: Point, c: Point):
        self.inputs = [a, b, c]
        self.outputs = None

    def construct(self, x: Point):
        self.outputs = [x]

    def conditions(self):
        a, b, c = self.inputs
        return [NotCollinear(a, b, c)]

    def conclusions(self):
        a, b, c = self.inputs
        x, = self.outputs
        return [Angle(a, b, c) - Angle(c, b, x)]


@register("deterministic")
class construct_circle(ConstructionRule):
    def __init__(self, a: Point, b: Point, c: Point):
        self.inputs = [a, b, c]
        self.outputs = None

    def construct(self, x: Point):
        self.outputs = [x]

    def conditions(self):
        a, b, c = self.inputs
        return [NotCollinear(a, b, c)]

    def conclusions(self):
        a, b, c = self.inputs
        x, = self.outputs
        return [
            Length(x, a) - Length(x, b),
            Length(x, b) - Length(x, c),
        ]


@register("deterministic")
class construct_circumcenter(ConstructionRule):
    def __init__(self, a: Point, b: Point, c: Point):
        self.inputs = [a, b, c]
        self.outputs = None

    def construct(self, x: Point):
        self.outputs = [x]

    def conditions(self):
        a, b, c = self.inputs
        return [NotCollinear(a, b, c)]

    def conclusions(self):
        a, b, c = self.inputs
        x, = self.outputs
        return [
            Length(x, a) - Length(x, b),
            Length(x, b) - Length(x, c),
        ]


@register("independent")
class construct_eq_quadrangle(ConstructionRule):
    def __init__(self):
        self.inputs = []
        self.outputs = None

    def construct(self, a: Point, b: Point, c: Point, d: Point):
        self.outputs = [a, b, c, d]

    def conclusions(self):
        a, b, c, d = self.outputs
        return [Length(a, d) - Length(b, c)]


@register("independent")
class construct_eq_trapezoid(ConstructionRule):
    def __init__(self):
        self.inputs = []
        self.outputs = None

    def construct(self, a: Point, b: Point, c: Point, d: Point):
        self.outputs = [a, b, c, d]

    def conclusions(self):
        a, b, c, d = self.outputs
        return [
            Length(a, d) - Length(b, c),
            Parallel(a, b, c, d),
            Angle(d, a, b) - Angle(a, b, c),
            Angle(b, c, d) - Angle(c, d, a),
        ]


@register("deterministic")
class construct_eq_triangle(ConstructionRule):
    def __init__(self, b: Point, c: Point):
        self.inputs = [b, c]
        self.outputs = None

    def construct(self, x: Point):
        self.outputs = [x]

    def conditions(self):
        b, c = self.inputs
        return [Different(b, c)]

    def conclusions(self):
        b, c = self.inputs
        x, = self.outputs
        return [
            Length(x, b) - Length(b, c),
            Length(b, c) - Length(c, x),
            Angle(x, b, c) - Angle(b, c, x),
            Angle(c, x, b) - Angle(x, b, c),
        ]


@register("nondeterministic")
class construct_eqangle2(ConstructionRule):
    def __init__(self, a: Point, b: Point, c: Point):
        self.inputs = [a, b, c]
        self.outputs = None

    def construct(self, x: Point):
        self.outputs = [x]

    def conditions(self):
        a, b, c = self.inputs
        return [NotCollinear(a, b, c)]

    def conclusions(self):
        a, b, c = self.inputs
        x, = self.outputs
        return [Angle(b, a, x) - Angle(x, c, b)]



@register("independent")
class construct_eqdia_quadrangle(ConstructionRule):
    def __init__(self):
        self.inputs = []
        self.outputs = None

    def construct(self, a: Point, b: Point, c: Point, d: Point):
        self.outputs = [a, b, c, d]

    def conclusions(self):
        a, b, c, d = self.outputs
        return [Length(b, d) - Length(a, c)]



@register("nondeterministic")
class construct_eqdistance(ConstructionRule):
    def __init__(self, a: Point, b: Point, c: Point):
        self.inputs = [a, b, c]
        self.outputs = None

    def construct(self, x: Point):
        self.outputs = [x]

    def conditions(self):
        a, b, c = self.inputs
        return [Different(b, c)]

    def conclusions(self):
        a, b, c = self.inputs
        x, = self.outputs
        return [Length(x, a) - Length(b, c)]


# @register("AG")
# class construct_eqdistance2(ConstructionRule):
#     def __init__(self, a: Point, b: Point, c: Point, alpha: float):
#         self.inputs = [a, b, c, alpha]
#         self.outputs = None

#     def construct(self, x: Point):
#         self.outputs = [x]

#     def conditions(self):
#         a, b, c, alpha = self.inputs
#         return [Different(b, c)]

#     def conclusions(self):
#         a, b, c, alpha = self.inputs
#         x, = self.outputs
#         return [Length(x, a) - sympy.simplify(alpha) * Length(b, c)]


# @register("AG")
# class construct_eqdistance3(ConstructionRule):
#     def __init__(self, a: Point, alpha: float):
#         self.inputs = [a, alpha]
#         self.outputs = None

#     def construct(self, x: Point):
#         self.outputs = [x]

#     def conclusions(self):
#         a, alpha = self.inputs
#         x, = self.outputs
#         return [Length(x, a) - sympy.simplify(alpha)]


@register("nondeterministic")
class construct_foot(ConstructionRule):
    def __init__(self, a: Point, b: Point, c: Point):
        self.inputs = [a, b, c]
        self.outputs = None

    def construct(self, x: Point):
        self.outputs = [x]

    def conditions(self):
        a, b, c = self.inputs
        return [NotCollinear(a, b, c)]

    def conclusions(self):
        a, b, c = self.inputs
        x, = self.outputs
        return [Perpendicular(x, a, b, c), Collinear(x, b, c)]


@register("independent")
class construct_free(ConstructionRule):
    def __init__(self):
        self.inputs = []
        self.outputs = None

    def construct(self, a: Point):
        self.outputs = [a]


@register("deterministic")
class construct_incenter(ConstructionRule):
    def __init__(self, a: Point, b: Point, c: Point):
        self.inputs = [a, b, c]
        self.outputs = None

    def construct(self, x: Point):
        self.outputs = [x]

    def conditions(self):
        a, b, c = self.inputs
        return [NotCollinear(a, b, c)]

    def conclusions(self):
        a, b, c = self.inputs
        x, = self.outputs
        return [
            Angle(b, a, x) - Angle(x, a, c),
            Angle(a, c, x) - Angle(x, c, b),
            Angle(c, b, x) - Angle(x, b, a),
        ]


@register("deterministic")
class construct_incenter2(ConstructionRule):
    def __init__(self, a: Point, b: Point, c: Point):
        self.inputs = [a, b, c]
        self.outputs = None

    def construct(self, x: Point, y: Point, z: Point, i: Point):
        self.outputs = [x, y, z, i]

    def conditions(self):
        a, b, c = self.inputs
        return [NotCollinear(a, b, c)]

    def conclusions(self):
        a, b, c = self.inputs
        x, y, z, i = self.outputs
        return [
            Angle(b, a, i) - Angle(i, a, c),
            Angle(a, c, i) - Angle(i, c, b),
            Angle(c, b, i) - Angle(i, b, a),
            Collinear(x, b, c),
            Perpendicular(i, x, b, c),
            Collinear(y, c, a),
            Perpendicular(i, y, c, a),
            Collinear(z, a, b),
            Perpendicular(i, z, a, b),
            Length(i, x) - Length(i, y),
            Length(i, y) - Length(i, z),
        ]


@register("deterministic")
class construct_excenter(ConstructionRule):
    def __init__(self, a: Point, b: Point, c: Point):
        self.inputs = [a, b, c]
        self.outputs = None

    def construct(self, x: Point):
        self.outputs = [x]

    def conditions(self):
        a, b, c = self.inputs
        return [NotCollinear(a, b, c)]

    def conclusions(self):
        a, b, c = self.inputs
        x, = self.outputs
        return [
            Angle(b, a, x) - Angle(x, a, c),
            Angle(a, b, x) - (Angle(a, b, c) / 2 + pi / 2),
            Angle(a, c, x) - (Angle(a, c, b) / 2 + pi / 2),
        ]


@register("deterministic")
class construct_excenter2(ConstructionRule):
    def __init__(self, a: Point, b: Point, c: Point):
        self.inputs = [a, b, c]
        self.outputs = None

    def construct(self, x: Point, y: Point, z: Point, i: Point):
        self.outputs = [x, y, z, i]

    def conditions(self):
        a, b, c = self.inputs
        return [NotCollinear(a, b, c)]

    def conclusions(self):
        a, b, c = self.inputs
        x, y, z, i = self.outputs
        return [
            Angle(b, a, i) - Angle(i, a, c),
            Angle(a, b, i) - (Angle(a, b, c) / 2 + pi / 2),
            Angle(a, c, i) - (Angle(a, c, b) / 2 + pi / 2),
            Collinear(x, b, c),
            Perpendicular(i, x, b, c),
            Collinear(y, c, a),
            Perpendicular(i, y, c, a),
            Collinear(z, a, b),
            Perpendicular(i, z, a, b),
            Length(i, x) - Length(i, y),
            Length(i, y) - Length(i, z),
        ]


@register("deterministic")
class construct_centroid(ConstructionRule):
    def __init__(self, a: Point, b: Point, c: Point):
        self.inputs = [a, b, c]
        self.outputs = None

    def construct(self, x: Point, y: Point, z: Point, i: Point):
        self.outputs = [x, y, z, i]

    def conditions(self):
        a, b, c = self.inputs
        return [NotCollinear(a, b, c)]

    def conclusions(self):
        a, b, c = self.inputs
        x, y, z, i = self.outputs
        return [
            Collinear(x, b, c),
            Length(x, b) - Length(x, c),
            Collinear(y, c, a),
            Length(y, c) - Length(y, a),
            Collinear(z, a, b),
            Length(z, a) - Length(z, b),
            Collinear(a, x, i),
            Collinear(b, y, i),
            Collinear(c, z, i),
        ]


@register("deterministic")
class construct_intersection_cc(ConstructionRule):
    def __init__(self, o: Point, w: Point, a: Point):
        self.inputs = [o, w, a]
        self.outputs = None

    def construct(self, x: Point):
        self.outputs = [x]

    def conditions(self):
        o, w, a = self.inputs
        return [NotCollinear(o, w, a)]

    def conclusions(self):
        o, w, a = self.inputs
        x, = self.outputs
        return [
            Length(o, a) - Length(o, x),
            Length(w, a) - Length(w, x),
        ]


@register("deterministic")
class construct_intersection_lc(ConstructionRule):
    def __init__(self, a: Point, o: Point, b: Point):
        self.inputs = [a, o, b]
        self.outputs = None

    def construct(self, x: Point):
        self.outputs = [x]

    def conditions(self):
        a, o, b = self.inputs
        return [
            Different(a, b),
            Different(o, b),
            Not(Perpendicular(b, o, b, a)),
        ]

    def conclusions(self):
        a, o, b = self.inputs
        x, = self.outputs
        return [
            Collinear(x, a, b),
            Length(o, b) - Length(o, x),
        ]

# TODO
@register("deterministic")
class construct_intersection_ll(ConstructionRule):
    def __init__(self, a: Point, b: Point, c: Point, d: Point):
        self.inputs = [a, b, c, d]
        self.outputs = None

    def construct(self, x: Point):
        self.outputs = [x]

    def conditions(self):
        a, b, c, d = self.inputs
        return [Not(Parallel(a, b, c, d)), Not(Collinear(a, b, c, d))]

    def conclusions(self):
        a, b, c, d = self.inputs
        x, = self.outputs
        return [Collinear(x, a, b), Collinear(x, c, d)]

# TODO
@register("deterministic")
class construct_intersection_lp(ConstructionRule):
    def __init__(self, a: Point, b: Point, c: Point, m: Point, n: Point):
        self.inputs = [a, b, c, m, n]
        self.outputs = None

    def construct(self, x: Point):
        self.outputs = [x]

    def conditions(self):
        a, b, c, m, n = self.inputs
        return [
            Not(Parallel(m, n, a, b)),
            NotCollinear(a, b, c),
            NotCollinear(c, m, n),
        ]

    def conclusions(self):
        a, b, c, m, n = self.inputs
        x, = self.outputs
        return [Collinear(x, a, b), Parallel(c, x, m, n)]


# TODO
@register("deterministic")
class construct_intersection_lt(ConstructionRule):
    def __init__(self, a: Point, b: Point, c: Point, d: Point, e: Point):
        self.inputs = [a, b, c, d, e]
        self.outputs = None

    def construct(self, x: Point):
        self.outputs = [x]

    def conditions(self):
        a, b, c, d, e = self.inputs
        return [
            NotCollinear(a, b, c),
            Not(Perpendicular(a, b, d, e)),
        ]

    def conclusions(self):
        a, b, c, d, e = self.inputs
        x, = self.outputs
        return [Collinear(x, a, b), Perpendicular(x, c, d, e)]

# TODO
@register("deterministic")
class construct_intersection_pp(ConstructionRule):
    def __init__(self, a: Point, b: Point, c: Point, d: Point, e: Point, f: Point):
        self.inputs = [a, b, c, d, e, f]
        self.outputs = None

    def construct(self, x: Point):
        self.outputs = [x]

    def conditions(self):
        a, b, c, d, e, f = self.inputs
        return [
            Different(a, d),
            Not(Parallel(b, c, e, f)),
        ]

    def conclusions(self):
        a, b, c, d, e, f = self.inputs
        x, = self.outputs
        return [
            Parallel(x, a, b, c),
            Parallel(x, d, e, f),
        ]

# TODO
@register("deterministic")
class construct_intersection_tt(ConstructionRule):
    def __init__(self, a: Point, b: Point, c: Point, d: Point, e: Point, f: Point):
        self.inputs = [a, b, c, d, e, f]
        self.outputs = None

    def construct(self, x: Point):
        self.outputs = [x]

    def conditions(self):
        a, b, c, d, e, f = self.inputs
        return [
            Different(a, d),
            Not(Parallel(b, c, e, f)),
        ]

    def conclusions(self):
        a, b, c, d, e, f = self.inputs
        x, = self.outputs
        return [
            Perpendicular(x, a, b, c),
            Perpendicular(x, d, e, f),
        ]


@register("independent")
class construct_iso_triangle(ConstructionRule):
    def __init__(self):
        self.inputs = []
        self.outputs = None

    def construct(self, a: Point, b: Point, c: Point):
        self.outputs = [a, b, c]

    def conclusions(self):
        a, b, c = self.outputs
        return [
            Length(a, b) - Length(a, c),
            Angle(a, b, c) - Angle(b, c, a),
        ]


@register("nondeterministic")
class construct_lc_tangent(ConstructionRule):
    def __init__(self, a: Point, o: Point):
        self.inputs = [a, o]
        self.outputs = None

    def construct(self, x: Point):
        self.outputs = [x]
        
    def conditions(self):
        a, o = self.inputs
        return [Different(a, o)]

    def conclusions(self):
        a, o = self.inputs
        x, = self.outputs
        return [Perpendicular(a, x, a, o)]


@register("deterministic")
class construct_midpoint(ConstructionRule):
    def __init__(self, a: Point, b: Point):
        self.inputs = [a, b]
        self.outputs = None

    def construct(self, x: Point):
        self.outputs = [x]

    def conditions(self):
        a, b = self.inputs
        return [Different(a, b)]

    def conclusions(self):
        a, b = self.inputs
        x, = self.outputs
        return [
            Collinear(x, a, b),
            Length(x, a) - Length(x, b),
        ]


@register("deterministic")
class construct_mirror(ConstructionRule):
    def __init__(self, a: Point, b: Point):
        self.inputs = [a, b]
        self.outputs = None

    def construct(self, x: Point):
        self.outputs = [x]

    def conditions(self):
        a, b = self.inputs
        return [Different(a, b)]

    def conclusions(self):
        a, b = self.inputs
        x, = self.outputs
        return [
            Length(b, a) - Length(b, x),
            Collinear(x, a, b),
        ]


@register("deterministic")
class construct_nsquare(ConstructionRule):
    def __init__(self, a: Point, b: Point):
        self.inputs = [a, b]
        self.outputs = None

    def construct(self, x: Point):
        self.outputs = [x]

    def conditions(self):
        a, b = self.inputs
        return [Different(a, b)]

    def conclusions(self):
        a, b = self.inputs
        x, = self.outputs
        return [
            Length(x, a) - Length(a, b),
            Perpendicular(x, a, a, b),
        ]

# TODO
@register("nondeterministic")
class construct_on_aline(ConstructionRule):
    def __init__(self, a: Point, b: Point, c: Point, d: Point, e: Point):
        self.inputs = [a, b, c, d, e]
        self.outputs = None

    def construct(self, x: Point):
        self.outputs = [x]

    def conditions(self):
        a, b, c, d, e = self.inputs
        return [NotCollinear(c, d, e)]

    def conclusions(self):
        a, b, c, d, e = self.inputs
        x, = self.outputs
        return (
            Angle(x, a, b) - Angle(c, d, e),
            Angle(x, a, b) + Angle(c, d, e) - pi,
        )



# @register("AG")
# class construct_on_aline2(ConstructionRule):
#     def __init__(self, x, a, b, c, d, e):
#         self.x, self.a, self.b, self.c, self.d, self.e = x, a, b, c, d, e
    
#     def arguments(self):
#         return [self.a, self.b, self.c, self.d, self.e]
        
#     def constructed_points(self):
#         return [self.x]

#     def conditions(self):
#         return [
#             NotCollinear(self.c, self.d, self.e),
#             Different(self.a, self.b),
#             Different(self.c, self.d),
#             Different(self.c, self.e),
#         ]

#     def conclusions(self):
#         return [Angle(self.x, self.a, self.b) + Angle(self.c, self.d, self.e) - pi]


@register("nondeterministic")
class construct_on_bline(ConstructionRule):
    def __init__(self, a: Point, b: Point):
        self.inputs = [a, b]
        self.outputs = None

    def construct(self, x: Point):
        self.outputs = [x]

    def conditions(self):
        a, b = self.inputs
        return [Different(a, b)]

    def conclusions(self):
        a, b = self.inputs
        x, = self.outputs
        return [
            Length(x, a) - Length(x, b),
            Angle(x, a, b) - Angle(a, b, x),
        ]


@register("nondeterministic")
class construct_on_circle(ConstructionRule):
    def __init__(self, o: Point, a: Point):
        self.inputs = [o, a]
        self.outputs = None

    def construct(self, x: Point):
        self.outputs = [x]

    def conditions(self):
        o, a = self.inputs
        return [Different(o, a)]

    def conclusions(self):
        o, a = self.inputs
        x, = self.outputs
        return [Length(o, x) - Length(o, a)]


@register("nondeterministic")
class construct_on_line(ConstructionRule):
    def __init__(self, a: Point, b: Point):
        self.inputs = [a, b]
        self.outputs = None

    def construct(self, x: Point):
        self.outputs = [x]

    def conditions(self):
        a, b = self.inputs
        return [Different(a, b)]

    def conclusions(self):
        a, b = self.inputs
        x, = self.outputs
        return [Collinear(x, a, b)]


@register("nondeterministic")
class construct_on_pline(ConstructionRule):
    def __init__(self, a: Point, b: Point, c: Point):
        self.inputs = [a, b, c]
        self.outputs = None

    def construct(self, x: Point):
        self.outputs = [x]

    def conditions(self):
        a, b, c = self.inputs
        return [Different(b, c), NotCollinear(a, b, c)]

    def conclusions(self):
        a, b, c = self.inputs
        x, = self.outputs
        return [Parallel(x, a, b, c)]


@register("nondeterministic")
class construct_on_tline(ConstructionRule):
    def __init__(self, a: Point, b: Point, c: Point):
        self.inputs = [a, b, c]
        self.outputs = None

    def construct(self, x: Point):
        self.outputs = [x]

    def conditions(self):
        a, b, c = self.inputs
        return [Different(b, c)]

    def conclusions(self):
        a, b, c = self.inputs
        x, = self.outputs
        return [Perpendicular(x, a, b, c)]


@register("deterministic")
class construct_orthocenter(ConstructionRule):
    def __init__(self, a: Point, b: Point, c: Point):
        self.inputs = [a, b, c]
        self.outputs = None

    def construct(self, x: Point):
        self.outputs = [x]

    def conditions(self):
        a, b, c = self.inputs
        return [NotCollinear(a, b, c)]

    def conclusions(self):
        a, b, c = self.inputs
        x, = self.outputs
        return [
            Perpendicular(x, a, b, c),
            Perpendicular(x, b, c, a),
            Perpendicular(x, c, a, b),
        ]


@register("deterministic")
class construct_parallelogram(ConstructionRule):
    def __init__(self, a: Point, b: Point, c: Point):
        self.inputs = [a, b, c]
        self.outputs = None

    def construct(self, x: Point):
        self.outputs = [x]

    def conditions(self):
        a, b, c = self.inputs
        return [NotCollinear(a, b, c)]

    def conclusions(self):
        a, b, c = self.inputs
        x, = self.outputs
        return [
            Parallel(a, b, c, x),
            Parallel(a, x, b, c),
            Length(a, b) - Length(c, x),
            Length(a, x) - Length(b, c),
        ]


@register("independent")
class construct_pentagon(ConstructionRule):
    def __init__(self):
        self.inputs = []
        self.outputs = None

    def construct(self, a: Point, b: Point, c: Point, d: Point, e: Point):
        self.outputs = [a, b, c, d, e]


@register("deterministic")
class construct_psquare(ConstructionRule):
    def __init__(self, a: Point, b: Point):
        self.inputs = [a, b]
        self.outputs = None

    def construct(self, x: Point):
        self.outputs = [x]

    def conditions(self):
        a, b = self.inputs
        return [Different(a, b)]

    def conclusions(self):
        a, b = self.inputs
        x, = self.outputs
        return [
            Length(x, a) - Length(a, b),
            Perpendicular(x, a, a, b),
        ]


@register("independent")
class construct_quadrangle(ConstructionRule):
    def __init__(self):
        self.inputs = []
        self.outputs = None

    def construct(self, a: Point, b: Point, c: Point, d: Point):
        self.outputs = [a, b, c, d]


@register("independent")
class construct_r_trapezoid(ConstructionRule):
    def __init__(self):
        self.inputs = []
        self.outputs = None

    def construct(self, a: Point, b: Point, c: Point, d: Point):
        self.outputs = [a, b, c, d]

    def conclusions(self):
        a, b, c, d = self.outputs
        return [
            Perpendicular(a, b, a, d),
            Parallel(a, b, c, d),
        ]


@register("independent")
class construct_r_triangle(ConstructionRule):
    def __init__(self):
        self.inputs = []
        self.outputs = None

    def construct(self, a: Point, b: Point, c: Point):
        self.outputs = [a, b, c]

    def conclusions(self):
        a, b, c = self.outputs
        return [Perpendicular(a, b, a, c)]


@register("independent")
class construct_rectangle(ConstructionRule):
    def __init__(self):
        self.inputs = []
        self.outputs = None

    def construct(self, a: Point, b: Point, c: Point, d: Point):
        self.outputs = [a, b, c, d]

    def conclusions(self):
        a, b, c, d = self.outputs
        return [
            Perpendicular(a, b, b, c),
            Parallel(a, b, c, d),
            Parallel(a, d, b, c),
            Perpendicular(a, b, a, d),
            Length(a, b) - Length(c, d),
            Length(a, d) - Length(b, c),
            Length(a, c) - Length(b, d),
        ]


@register("deterministic")
class construct_reflect(ConstructionRule):
    def __init__(self, a: Point, b: Point, c: Point):
        self.inputs = [a, b, c]
        self.outputs = None

    def construct(self, x: Point):
        self.outputs = [x]

    def conditions(self):
        a, b, c = self.inputs
        return [Different(b, c), NotCollinear(a, b, c)]

    def conclusions(self):
        a, b, c = self.inputs
        x, = self.outputs
        return [
            Perpendicular(b, c, a, x),
            Length(a, b) - Length(b, x),
            Length(a, c) - Length(c, x),
        ]


@register("independent")
class construct_risos(ConstructionRule):
    def __init__(self):
        self.inputs = []
        self.outputs = None

    def construct(self, a: Point, b: Point, c: Point):
        self.outputs = [a, b, c]

    def conclusions(self):
        a, b, c = self.outputs
        return [
            Angle(a, b, c) - Angle(b, c, a),
            Perpendicular(a, b, a, c),
            Length(a, b) - Length(a, c),
        ]


@register("nondeterministic")
class construct_s_angle(ConstructionRule):
    def __init__(self, a: Point, b: Point, alpha: float):
        self.inputs = [a, b, alpha]
        self.outputs = None

    def construct(self, x: Point):
        self.outputs = [x]

    def conditions(self):
        a, b, alpha = self.inputs
        return [Different(a, b)]

    def conclusions(self):
        a, b, alpha = self.inputs
        x, = self.outputs
        return [Angle(a, b, x) - sympy.simplify(sympy.Rational(abs(alpha), 180) * pi)]


@register("independent")
class construct_segment(ConstructionRule):
    def __init__(self):
        self.inputs = []
        self.outputs = None

    def construct(self, a: Point, b: Point):
        self.outputs = [a, b]


# @register("independent")
# class construct_s_segment(ConstructionRule):
#     def __init__(self, alpha: float):
#         self.inputs = [alpha]
#         self.outputs = None

#     def construct(self, a: Point, b: Point):
#         self.outputs = [a, b]

#     def conclusions(self):
#         alpha, = self.inputs
#         a, b = self.outputs
#         return [Length(a, b) - sympy.simplify(alpha)]


@register("deterministic")
class construct_shift(ConstructionRule):
    def __init__(self, b: Point, c: Point, d: Point):
        self.inputs = [b, c, d]
        self.outputs = None

    def construct(self, x: Point):
        self.outputs = [x]

    def conditions(self):
        b, c, d = self.inputs
        return [Different(d, b)]

    def conclusions(self):
        b, c, d = self.inputs
        x, = self.outputs
        return [
            Length(x, b) - Length(c, d),
            Length(x, c) - Length(b, d),
        ]


@register("deterministic")
class construct_square(ConstructionRule):
    def __init__(self, a: Point, b: Point):
        self.inputs = [a, b]
        self.outputs = None

    def construct(self, x: Point, y: Point):
        self.outputs = [x, y]

    def conditions(self):
        a, b = self.inputs
        return [Different(a, b)]

    def conclusions(self):
        a, b = self.inputs
        x, y = self.outputs
        return [
            Perpendicular(a, b, b, x),
            Length(a, b) - Length(b, x),
            Parallel(a, b, x, y),
            Parallel(a, y, b, x),
            Perpendicular(a, y, y, x),
            Length(b, x) - Length(x, y),
            Length(x, y) - Length(y, a),
            Perpendicular(a, x, b, y),
            Length(a, x) - Length(b, y),
        ]


@register("independent")
class construct_isquare(ConstructionRule):
    def __init__(self):
        self.inputs = []
        self.outputs = None

    def construct(self, a: Point, b: Point, c: Point, d: Point):
        self.outputs = [a, b, c, d]

    def conclusions(self):
        a, b, c, d = self.outputs
        return [
            Perpendicular(a, b, b, c),
            Length(a, b) - Length(b, c),
            Parallel(a, b, c, d),
            Parallel(a, d, b, c),
            Perpendicular(a, d, d, c),
            Length(b, c) - Length(c, d),
            Length(c, d) - Length(d, a),
            Perpendicular(a, c, b, d),
            Length(a, c) - Length(b, d),
        ]


@register("independent")
class construct_trapezoid(ConstructionRule):
    def __init__(self):
        self.inputs = []
        self.outputs = None

    def construct(self, a: Point, b: Point, c: Point, d: Point):
        self.outputs = [a, b, c, d]

    def conclusions(self):
        a, b, c, d = self.outputs
        return [Parallel(a, b, c, d)]


@register("independent")
class construct_triangle(ConstructionRule):
    def __init__(self):
        self.inputs = []
        self.outputs = None

    def construct(self, a: Point, b: Point, c: Point):
        self.outputs = [a, b, c]


@register("independent")
class construct_triangle12(ConstructionRule):
    def __init__(self):
        self.inputs = []
        self.outputs = None

    def construct(self, a: Point, b: Point, c: Point):
        self.outputs = [a, b, c]

    def conclusions(self):
        a, b, c = self.outputs
        return [Length(a, b) / Length(a, c) - sympy.Rational(1, 2)]


@register("deterministic")
class construct_2l1c(ConstructionRule):
    def __init__(self, a: Point, b: Point, c: Point, o: Point):
        self.inputs = [a, b, c, o]
        self.outputs = None

    def construct(self, x: Point, y: Point, z: Point, i: Point):
        self.outputs = [x, y, z, i]

    def conditions(self):
        a, b, c, o = self.inputs
        return [
            Length(o, a) - Length(o, b),
            NotCollinear(a, b, c),
        ]

    def conclusions(self):
        a, b, c, o = self.inputs
        x, y, z, i = self.outputs
        return [
            Collinear(x, a, c),
            Collinear(y, b, c),
            Length(o, a) - Length(o, z),
            Collinear(i, o, z),
            Length(i, x) - Length(i, y),
            Length(i, y) - Length(i, z),
            Perpendicular(i, x, a, c),
            Perpendicular(i, y, b, c),
        ]


# @register("AG")
# class construct_e5128(ConstructionRule):
#     def __init__(self, a: Point, b: Point, c: Point, d: Point):
#         self.inputs = [a, b, c, d]
#         self.outputs = None

#     def construct(self, x: Point, y: Point):
#         self.outputs = [x, y]

#     def conditions(self):
#         a, b, c, d = self.inputs
#         return [
#             Length(c, b) - Length(c, d),
#             Perpendicular(b, c, b, a),
#         ]

#     def conclusions(self):
#         a, b, c, d = self.inputs
#         x, y = self.outputs
#         return [
#             Length(c, b) - Length(c, x),
#             Collinear(y, a, b),
#             Collinear(x, y, d),
#             Angle(b, a, d) - Angle(a, x, y),
#         ]


# @register("AG")
# class construct_3peq(ConstructionRule):
#     def __init__(self, a: Point, b: Point, c: Point):
#         self.inputs = [a, b, c]
#         self.outputs = None

#     def construct(self, x: Point, y: Point, z: Point):
#         self.outputs = [x, y, z]

#     def conditions(self):
#         a, b, c = self.inputs
#         return [NotCollinear(a, b, c)]

#     def conclusions(self):
#         a, b, c = self.inputs
#         x, y, z = self.outputs
#         return [
#             Collinear(z, b, c),
#             Collinear(x, a, b),
#             Collinear(y, a, c),
#             Collinear(x, y, z),
#             Length(z, x) - Length(z, y),
#         ]


@register("deterministic")
class construct_trisect(ConstructionRule):
    def __init__(self, a: Point, b: Point, c: Point):
        self.inputs = [a, b, c]
        self.outputs = None

    def construct(self, x: Point, y: Point):
        self.outputs = [x, y]

    def conditions(self):
        a, b, c = self.inputs
        return [NotCollinear(a, b, c)]

    def conclusions(self):
        a, b, c = self.inputs
        x, y = self.outputs
        return [
            Angle(a, b, x) - Angle(x, b, y),
            Angle(x, b, y) - Angle(y, b, c),
            Collinear(x, a, c),
            Collinear(y, a, c),
        ]


@register("deterministic")
class construct_trisegment(ConstructionRule):
    def __init__(self, a: Point, b: Point):
        self.inputs = [a, b]
        self.outputs = None

    def construct(self, x: Point, y: Point):
        self.outputs = [x, y]

    def conditions(self):
        a, b = self.inputs
        return [Different(a, b)]

    def conclusions(self):
        a, b = self.inputs
        x, y = self.outputs
        return [
            Length(a, x) - Length(x, y),
            Length(x, y) - Length(y, b),
            Collinear(x, a, b),
            Collinear(y, a, b),
        ]


@register("nondeterministic")
class construct_on_dia(ConstructionRule):
    def __init__(self, a: Point, b: Point):
        self.inputs = [a, b]
        self.outputs = None

    def construct(self, x: Point):
        self.outputs = [x]

    def conditions(self):
        a, b = self.inputs
        return [Different(a, b)]

    def conclusions(self):
        a, b = self.inputs
        x, = self.outputs
        return [Perpendicular(x, a, x, b)]


@register("independent")
class construct_ieq_triangle(ConstructionRule):
    def __init__(self):
        self.inputs = []
        self.outputs = None

    def construct(self, a: Point, b: Point, c: Point):
        self.outputs = [a, b, c]

    def conclusions(self):
        a, b, c = self.outputs
        return [
            Length(a, b) - Length(b, c),
            Length(b, c) - Length(c, a),
            Angle(b, a, c) - Angle(a, c, b),
            Angle(a, c, b) - Angle(c, b, a),
        ]


@register("nondeterministic")
class construct_on_opline(ConstructionRule):
    def __init__(self, a: Point, b: Point):
        self.inputs = [a, b]
        self.outputs = None

    def construct(self, x: Point):
        self.outputs = [x]

    def conditions(self):
        a, b = self.inputs
        return [Different(a, b)]

    def conclusions(self):
        a, b = self.inputs
        x, = self.outputs
        return [Collinear(x, a, b)]


@register("deterministic")
class construct_cc_tangent0(ConstructionRule):
    def __init__(self, o: Point, a: Point, w: Point, b: Point):
        self.inputs = [o, a, w, b]
        self.outputs = None

    def construct(self, x: Point, y: Point):
        self.outputs = [x, y]

    def conditions(self):
        o, a, w, b = self.inputs
        return [
            Different(o, a),
            Different(w, b),
            Different(o, w),
        ]

    def conclusions(self):
        o, a, w, b = self.inputs
        x, y = self.outputs
        return [
            Length(o, x) - Length(o, a),
            Length(w, y) - Length(w, b),
            Perpendicular(x, o, x, y),
            Perpendicular(y, w, y, x),
        ]
        

@register("deterministic")
class construct_cc_tangent(ConstructionRule):
    def __init__(self, o: Point, a: Point, w: Point, b: Point):
        self.inputs = [o, a, w, b]
        self.outputs = None

    def construct(self, x: Point, y: Point, z: Point, i: Point):
        self.outputs = [x, y, z, i]

    def conditions(self):
        o, a, w, b = self.inputs
        return [
            Different(o, a),
            Different(w, b),
            Different(o, w),
        ]

    def conclusions(self):
        o, a, w, b = self.inputs
        x, y, z, i = self.outputs
        return [
            Length(o, x) - Length(o, a),
            Length(w, y) - Length(w, b),
            Perpendicular(x, o, x, y),
            Perpendicular(y, w, y, x),
            Length(o, z) - Length(o, a),
            Length(w, i) - Length(w, b),
            Perpendicular(z, o, z, i),
            Perpendicular(i, w, i, z),
        ]


@register("nondeterministic")
class construct_eqangle3(ConstructionRule):
    def __init__(self, a: Point, b: Point, d: Point, e: Point, f: Point):
        self.inputs = [a, b, d, e, f]
        self.outputs = None

    def construct(self, x: Point):
        self.outputs = [x]

    def conditions(self):
        a, b, d, e, f = self.inputs
        return [
            NotCollinear(d, e, f),
            Different(a, b),
            Different(d, e),
            Different(e, f),
        ]

    def conclusions(self):
        a, b, d, e, f = self.inputs
        x, = self.outputs
        return [Angle(a, x, b) - Angle(e, d, f)]


@register("deterministic")
class construct_tangent(ConstructionRule):
    def __init__(self, a: Point, o: Point, b: Point):
        self.inputs = [a, o, b]
        self.outputs = None

    def construct(self, x: Point, y: Point):
        self.outputs = [x, y]

    def conditions(self):
        a, o, b = self.inputs
        return [
            Different(o, a),
            Different(o, b),
            Different(a, b),
        ]

    def conclusions(self):
        a, o, b = self.inputs
        x, y = self.outputs
        return [
            Length(o, x) - Length(o, b),
            Perpendicular(a, x, o, x),
            Length(o, y) - Length(o, b),
            Perpendicular(a, y, o, y),
        ]


@register("nondeterministic")
class construct_on_circum(ConstructionRule):
    def __init__(self, a: Point, b: Point, c: Point):
        self.inputs = [a, b, c]
        self.outputs = None

    def construct(self, x: Point):
        self.outputs = [x]

    def conditions(self):
        a, b, c = self.inputs
        return [NotCollinear(a, b, c)]

    def conclusions(self):
        a, b, c = self.inputs
        x, = self.outputs
        return [Concyclic(a, b, c, x)]


@register("diagrammatic")
class construct_sameside(ConstructionRule):
    def __init__(self, a: Point, b: Point, c: Point):
        self.inputs = [a, b, c]
        self.outputs = None

    def construct(self, x: Point):
        self.outputs = [x]

    def conditions(self):
        a, b, c = self.inputs
        return [NotCollinear(a, b, c)]

    def conclusions(self):
        a, b, c = self.inputs
        x, = self.outputs
        return [SameSide(x, a, b, c)]


@register("diagrammatic")
class construct_opposingsides(ConstructionRule):
    def __init__(self, a: Point, b: Point, c: Point):
        self.inputs = [a, b, c]
        self.outputs = None

    def construct(self, x: Point):
        self.outputs = [x]

    def conditions(self):
        a, b, c = self.inputs
        return [NotCollinear(a, b, c)]

    def conclusions(self):
        a, b, c = self.inputs
        x, = self.outputs
        return [OppositeSide(x, a, b, c)]