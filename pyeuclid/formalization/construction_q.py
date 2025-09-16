from sympy import pi
import random
from .construction_rule import *
from .diagram import random_rfss, Circle, Segment, Ray
from .diagram import Point as Coord
import numpy as np
import math
# abuse Length and Angle class for type annotation for length and angle values

def sample_angle(low=0, high=pi, special_values=[]):
    values = [15, 30, 45, 60, 90, 120]
    values = [pi*item/180 for item in values]
    values += special_values
    values = [item for item in values if item > low and item < high]
    chosen = random.choice(values)
    return chosen

def sample_length(low=0, high=9999, special_values=[]):
    values = [1, 2, 3, 4, 5, 6, 8, 10, 12, 13]
    values += special_values
    values = [item for item in values if item > low and item < high]
    chosen = random.choice(values)
    return chosen

class ConstructionQ(ConstructionRule):
    def sample(angle_values=[], length_values=[]):
        raise NotImplementedError()
    
    def point2coord(self, point):
        return self.diagram.name2point[point.name]
    
    def __str__(self):
        class_name = self.__class__.__name__
        params = self.inputs + getattr(self, "params", [])
        inputs = ",".join([str(item) for item in params]) 
        outputs = ",".join(str(out) for out in self.outputs)
        return f"{outputs} = {class_name}({inputs})"
        
@register("independent")
class construct_segment_q(ConstructionQ):
    def __init__(self, ab:float = None, diagram=None):
        self.inputs = []
        self.ab = ab
        self.diagram = diagram
        
    def construct(self, a: Point, b: Point):
        self.outputs = [a, b]
        self.a, self.b = a, b
        return [self.ab], []
    
    def sample(self, angle_values=[], length_values=[]):
        ab = sample_length()
        self.ab = ab
        self.params = [ab]
        return [ab], []

    def conclusions(self):
        a, b = self.outputs
        return [
            Length(a, b) - sympy.simplify(self.ab)
        ]
        
    def sketch(self) -> list[Point]:
        a = Coord(0.0, 0.0)
        b = Coord(1.0, 0.0)
        a, b = random_rfss(a, b, scale=self.ab)
        return [a, b]
        
    def draw(self):
        return [Segment(self.point2coord(self.a), self.point2coord(self.b))], []
    

@register("nondeterministic")
class construct_angle_counterclockwise(ConstructionQ):
    def __init__(self, a: Point, b:Point, xab:float=None, diagram=None):
        self.inputs = [a, b]
        self.a = a
        self.b = b
        self.xab = xab
        self.diagram = diagram
        
    def construct(self, x: Point):
        self.x = x
        self.outputs = [x]
    
    def sample(self, angle_values=[], length_values=[]):
        self.xab = sample_angle(special_values=angle_values)
        self.params = [self.xab]
        return [], [self.xab]

    def conditions(self):
        return [Different2(self.a, self.b)]

    def conclusions(self):
        return [Angle(self.b, self.a, self.x) - self.xab]
    
    def sketch(self):
        a, b = self.point2coord(self.a), self.point2coord(self.b)
        angle = float(self.xab)
        # 2) compute the baseline direction at a: angle of vector a→b
        dx_ab = b.x - a.x
        dy_ab = b.y - a.y
        ang_ab = np.arctan2(dy_ab, dx_ab)

        # 3) rotate the baseline by +ang_cde so that ∠XAB = ang_cde
        ang_ax1 = ang_ab + angle

        # 4) place x one unit from a along that direction
        x1 = Coord(a.x + math.cos(ang_ax1), a.y + math.sin(ang_ax1))

        return Ray(a, x1)
    
    
    def draw(self):
        return [Segment(self.point2coord(self.a), self.point2coord(self.x)), Segment(self.point2coord(self.a), self.point2coord(self.b))], []
        
    
@register("nondeterministic")
class construct_angle_clockwise(ConstructionQ):
    def __init__(self, a: Point, b:Point, xab:float=None, diagram=None):
        self.inputs = [a, b]
        self.a = a
        self.b = b
        self.xab = xab
        self.diagram = diagram
        
    def construct(self, x: Point):
        self.x = x
        self.outputs = [x]
    
    def sample(self, angle_values=[], length_values=[]):
        self.xab = sample_angle(special_values=angle_values)
        self.params = [self.xab]
        return [], [self.xab]

    def conditions(self):
        return [Different2(self.a, self.b)]

    def conclusions(self):
        return [Angle(self.b, self.a, self.x) - self.xab]
    
    def sketch(self):
        a, b = self.point2coord(self.a), self.point2coord(self.b)
        angle = float(self.xab)
        # 2) compute the baseline direction at a: angle of vector a→b
        dx_ab = b.x - a.x
        dy_ab = b.y - a.y
        ang_ab = np.arctan2(dy_ab, dx_ab)

        # 3) rotate the baseline by +ang_cde so that ∠XAB = ang_cde
        ang_ax1 = ang_ab - angle

        # 4) place x one unit from a along that direction
        x1 = Coord(a.x + math.cos(ang_ax1), a.y + math.sin(ang_ax1))

        return Ray(a, x1)
    
    
    def draw(self):
        return [Segment(self.point2coord(self.a), self.point2coord(self.x)), Segment(self.point2coord(self.a), self.point2coord(self.b))], []
    
@register("nondeterministic")
class construct_point_on_circle(ConstructionQ):
    def __init__(self, o: Point, r:float=None, diagram=None):
        self.inputs = [o]
        self.o = o
        self.r = r
        self.diagram = diagram
        
    def sample(self, angle_values=[], length_values=[]):
        r = sample_length(special_values=length_values)
        self.r = r
        self.params = [r]
        return [self.r], []
        
    def construct(self, x: Point):
        self.x = x
        self.outputs = [x]
        
    def conclusions(self):
        x, = self.outputs
        return [Length(x, self.o)-self.r,]
    
    def sketch(self):
        return Circle(self.point2coord(self.o), self.r)
    
    def draw(self):
        return [Segment(self.point2coord(self.o), self.point2coord(self.x))], [] # Circle(self.point2coord(self.o), self.r)

@register("deterministic")
class construct_point_on_line(ConstructionQ):
    def __init__(self, a: Point, b:Point, l:float=None, diagram=None):
        self.a, self.b = a, b
        self.inputs = [a, b]
        self.l = l
        self.diagram = diagram
        
    def construct(self, x: Point):
        self.outputs = [x]
        self.x = x
        
    def sample(self, angle_values=[], length_values=[]):
        l = sample_length(special_values=length_values)
        self.l = l
        self.params = [l]
        return [self.l], []
    
    def conditions(self):
        return [Different2(self.a, self.b)]

    def conclusions(self):
        a, b = self.inputs
        x, = self.outputs
        return Collinear(x, a, b), Length(a, x) - self.l

    def sketch(self) -> Point:
        a, b, l = self.a, self.b, self.l
        a, b = self.diagram.name2point[self.a.name], self.diagram.name2point[self.b.name]
        a, b = np.array([a.x, a.y]), np.array([b.x, b.y])
        vec = b-a
        vec = vec/np.linalg.norm(vec)
        p = a + vec*l
        return Coord(p[0], p[1])
    
    def draw(self):
        return [Segment(self.point2coord(self.a), self.point2coord(self.x)), Segment(self.point2coord(self.a), self.point2coord(self.b))], []


@register("independent")
class construct_ieq_triangle_q(ConstructionQ):
    def __init__(self, l:float=None, diagram=None):
        self.l = l
        self.inputs = []
        self.diagram = diagram
    
    def construct(self, a: Point, b: Point, c: Point):
        self.a, self.b, self.c = a, b, c
        self.outputs = [a, b, c]
    
    def sample(self, angle_values=[], length_values=[]):
        l = sample_length(special_values=length_values)
        self.l = l
        self.params = [l]
        return [l], [pi/3]

    def conclusions(self):
        a, b, c = self.outputs
        return [
            EquilateralTriangle(a, b, c),
            Length(a, b) - self.l,
            Length(b, c) - self.l,
            Length(a, c) - self.l,
        ]
    
    def sketch(self) -> list[Point]:
        l = self.l
        a = Coord(0.0, 0.0)
        b = Coord(l, 0.0)
        c = Coord(l/2, l*3**0.5/2)
        a, b, c = random_rfss(a, b, c, scale=1)
        return [a, b, c]
    
    def draw(self):
        a, b, c = self.point2coord(self.a), self.point2coord(self.b), self.point2coord(self.c)
        return [Segment(a, b), Segment(a, c), Segment(b, c)], []

# @register("independent")
# class construct_triangle_asa(ConstructionQ):
#     def construct(self, a: Point, b: Point, c: Point):
#         self.outputs = [a, b, c]
#         self.abc = 1
    
#     def conclusions(self):
#         a, b, c = self.outputs
#         return [
#             Triangle(a, b, c),
#             Length(a, b) - self.ab,
#             Length(b, c) - self.bc,
#             Angle(a, b, c) - self.abc,
#         ]

# @register("independent")
# class construct_triangle_sas(ConstructionQ):
#     def construct(self, a: Point, b: Point, c: Point):
#         self.outputs = [a, b, c]
#         self.ab = sample_length()
#         self.bc = sample_length()
#         self.abc = sample_angle()
#         return [self.ab, self.bc], [self.abc]
    
#     def conclusions(self):
#         a, b, c = self.outputs
#         return [
#             Triangle(a, b, c),
#             Length(a, b) - self.ab,
#             Length(b, c) - self.bc,
#             Angle(a, b, c) - self.abc,
#         ]

# @register("independent")
# class construct_triangle_sss(ConstructionQ):
#     def construct(self, a: Point, b: Point, c: Point):
#         self.outputs = [a, b, c]
#         self.ab = sample_length()
#         self.bc = sample_length()
#         self.ac = sample_length(low=abs(self.ab-self.bc), high=self.ab+self.bc)
#         return [self.ab, self.bc, self.ac], []
    
#     def conclusions(self):
#         a, b, c = self.outputs
#         return [
#             Triangle(a, b, c),
#             Length(b, c) - self.bc,
#             Length(a, b) - self.ab,
#             Length(a, c) - self.ac
#         ]

@register("independent")
class construct_r_triangle_q(ConstructionQ):
    def __init__(self, ab:float=None, bc:float=None, diagram=None):
        self.ab = ab
        self.bc = bc
        self.inputs = []
        self.diagram = diagram
    
    def construct(self, a: Point, b: Point, c: Point):
        self.a, self.b, self.c = a, b, c
        self.outputs = [a, b, c]
    
    def sample(self, angle_values=[], length_values=[]):
        ab, bc = sample_length(special_values=length_values), sample_length(special_values=length_values)
        self.ab, self.bc = ab, bc
        self.params = [ab, bc]
        return [ab, bc], [pi/2]

    def conclusions(self):
        a, b, c = self.outputs
        return [
            Angle(a, b, c) - pi/2,
            Length(a, b) - self.ab,
            Length(b, c) - self.bc
        ]
    
    def sketch(self) -> list[Point]:
        b = Coord(0.0, 0.0)
        a = Coord(self.ab, 0.0)
        c = Coord(0.0, self.bc)
        a, b, c = random_rfss(a, b, c, scale=1)
        return [a, b, c]
    
    def draw(self):
        a, b, c = self.point2coord(self.a), self.point2coord(self.b), self.point2coord(self.c)
        return [Segment(a, b), Segment(a, c), Segment(b, c)], []


@register("independent")
class construct_eq_triangle_q(ConstructionQ):
    def __init__(self, bc:float=None, bac:float=None, diagram=None):
        self.bc = bc
        self.bac = bac
        self.inputs = []
        self.diagram = diagram
    
    def construct(self, a: Point, b: Point, c: Point):
        self.a, self.b, self.c = a, b, c
        self.outputs = [a, b, c]
    
    def sample(self, angle_values=[], length_values=[]):
        bc = sample_length(special_values=length_values)
        bac = sample_angle(special_values=angle_values)
        self.bc, self.bac = bc, bac
        self.params = [bc, bac]
        return [bc], [bac]

    def conclusions(self):
        a, b, c = self.outputs
        return [
            Angle(b, a, c) - self.bac,
            Length(b, c) - self.bc,
            Length(b, a) - Length(a, c)
        ]
    
    def sketch(self) -> list[Point]:
        b = Coord(0.0, 0.0)
        c = Coord(self.bc, 0.0)
        angle = (pi-self.bac)/2
        x= self.bc/2
        y = math.tan(angle.evalf())*x
        a = Coord(x, y)
        a, b, c = random_rfss(a, b, c, scale=1)
        return [a, b, c]
    
    def draw(self):
        a, b, c = self.point2coord(self.a), self.point2coord(self.b), self.point2coord(self.c)
        return [Segment(a, b), Segment(a, c), Segment(b, c)], []
        
@register("independent")
class construct_parallelogram_q(ConstructionQ):
    def __init__(self, ab:float=None, ad:float=None, bad:float=None, diagram=None):
        self.ab, self.ad, self.bad = ab, ad, bad
        self.inputs = []
        self.diagram = diagram
    
    def construct(self, a: Point, b: Point, c: Point, d:Point):
        self.a, self.b, self.c, self.d = a, b, c, d
        self.outputs = [a, b, c, d]
    
    def sample(self, angle_values=[], length_values=[]):
        ab = sample_length(special_values=length_values)
        ad = sample_length(special_values=length_values)
        bad = sample_angle(special_values=angle_values)
        self.ab, self.ad, self.bad = ab, ad, bad
        self.params = [ab, ad, bad]
        return [ab, ad], [bad, pi-bad]

    def conclusions(self):
        a, b, c, d = self.outputs
        return [
            Angle(b, a, d) - self.bad,
            Length(a, b) - self.ab,
            Length(a, d)- self.ad,
            Parallelogram(a, b, c, d)
        ]
    
    def sketch(self) -> list[Point]:
        a = Coord(0.0, 0.0)
        b = Coord(self.ab, 0.0)
        bad = self.bad.evalf()
        d = Coord(self.ad*math.cos(bad), self.ad*math.sin(bad))
        c = Coord(self.ab + self.ad*math.cos(bad), self.ad*math.sin(bad))
        a, b, c, d = random_rfss(a, b, c, d, scale=1)
        return [a, b, c, d]
    
    def draw(self):
        a, b, c, d = self.point2coord(self.a), self.point2coord(self.b), self.point2coord(self.c), self.point2coord(self.d)
        return [Segment(a, b), Segment(c, d), Segment(a, d), Segment(b, c)], []

@register("independent")
class construct_eq_trapezoid_q(ConstructionQ):
    def __init__(self, ab:float=None, ad:float=None, bad:float=None, diagram=None):
        self.ab, self.ad, self.bad = ab, ad, bad
        self.inputs = []
        self.diagram = diagram
    
    def construct(self, a: Point, b: Point, c: Point, d:Point):
        self.a, self.b, self.c, self.d = a, b, c, d
        self.outputs = [a, b, c, d]
    
    def sample(self, angle_values=[], length_values=[]):
        ab = sample_length(special_values=length_values)
        ad = sample_length(special_values=length_values)
        bad = sample_angle(special_values=angle_values)
        self.ab, self.ad, self.bad = ab, ad, bad
        self.params = [ab, ad, bad]
        return [ab, ad], [bad, pi-bad]

    def conclusions(self):
        a, b, c, d = self.outputs
        return [
            Angle(b, a, d) - self.bad,
            Length(a, b) - self.ab,
            Length(a, d) - self.ad,
            Length(a, d) - Length(b, c),
            Parallel(a, b, c, d),
            Trapezoid(a, b, c, d)
        ]
    
    def sketch(self) -> list[Point]:
        a = Coord(0.0, 0.0)
        b = Coord(self.ab, 0.0)
        bad = self.bad.evalf()
        d = Coord(self.ad*math.cos(bad), self.ad*math.sin(bad))
        c = Coord(self.ab - self.ad*math.cos(bad), self.ad*math.sin(bad))
        a, b, c, d = random_rfss(a, b, c, d, scale=1)
        return [a, b, c, d]
    
    def draw(self):
        a, b, c, d = self.point2coord(self.a), self.point2coord(self.b), self.point2coord(self.c), self.point2coord(self.d)
        return [Segment(a, b), Segment(c, d), Segment(a, d), Segment(b, c)], []

@register("independent")
class construct_r_trapezoid_q(ConstructionQ):
    def __init__(self, ab:float=None, ad:float=None, cd:float=None, diagram=None):
        self.ab, self.ad, self.cd = ab, ad, cd
        self.inputs = []
        self.diagram = diagram
    
    def construct(self, a: Point, b: Point, c: Point, d:Point):
        self.a, self.b, self.c, self.d = a, b, c, d
        self.outputs = [a, b, c, d]
    
    def sample(self, angle_values=[], length_values=[]):
        ab = sample_length(special_values=length_values)
        ad = sample_length(special_values=length_values)
        cd = sample_length(special_values=length_values)
        self.ab, self.ad, self.cd = ab, ad, cd
        self.params = [ab, ad, cd]
        return [ab, ad, cd], []

    def conclusions(self):
        a, b, c, d = self.outputs
        return [
            Length(a, b) - self.ab,
            Length(a, d) - self.ad,
            Length(c, d) - self.cd,
            Angle(b, a, d) - pi/2,
            Parallel(a, b, c, d),
            Trapezoid(a, b, c, d)
        ]
    
    def sketch(self) -> list[Point]:
        a = Coord(0.0, 0.0)
        b = Coord(self.ab, 0.0)
        d = Coord(0.0, self.ad)
        c = Coord(self.cd, self.ad)
        a, b, c, d = random_rfss(a, b, c, d, scale=1)
        return [a, b, c, d]
    
    def draw(self):
        a, b, c, d = self.point2coord(self.a), self.point2coord(self.b), self.point2coord(self.c), self.point2coord(self.d)
        return [Segment(a, b), Segment(c, d), Segment(a, d), Segment(b, c)], []
        
        
@register("independent")
class construct_square_q(ConstructionQ):
    def __init__(self, l:float=None, diagram=None):
        self.inputs = []
        self.outputs = None
        self.l = l
        self.diagram = diagram
        
    def sample(self, angle_values=[], length_values=[]):
        l = sample_length()
        self.l = l
        self.params = [l]
        return [self.l], [pi/2]

    def construct(self, a: Point, b: Point, c: Point, d: Point):
        self.outputs = [a, b, c, d]
        self.a, self.b, self.c, self.d = a, b, c, d
        
    def conclusions(self):
        a, b, c, d = self.outputs
        return [
            Square(a, b, c, d),
            Length(a, b) - self.l
        ]
        
    def sketch(self) -> list[Point]:
        a = Coord(0.0, 0.0)
        b = Coord(1.0, 0.0)
        c = Coord(1.0, 1.0)
        d = Coord(0.0, 1.0)
        a, b, c, d = random_rfss(a, b, c, d, scale=self.l)
        return [a, b, c, d]

    def draw(self):
        a, b, c, d = self.point2coord(self.a), self.point2coord(self.b), self.point2coord(self.c), self.point2coord(self.d)
        return [Segment(a, b), Segment(c, d), Segment(a, d), Segment(b, c)], []
    

        
@register("independent")
class construct_rectangle_q(ConstructionQ):
    def __init__(self, h:float=None, w:float=None, diagram=None):
        self.h = h
        self.w = w
        self.inputs = []
        self.diagram = diagram
    
    def construct(self, a: Point, b: Point, c: Point, d: Point):
        self.a, self.b, self.c, self.d = a, b, c, d
        self.outputs = [a, b, c, d]
    
    def sample(self, angle_values=[], length_values=[]):
        h = sample_length()
        w = sample_length()
        self.h = h
        self.w = w
        self.params = [h, w]
        return [self.h, self.w], [pi/2]

    def conclusions(self):
        a, b, c, d = self.outputs
        return [
            Rectangle(a, b, c, d),
            Length(a, b) - self.h,
            Length(a, d) - self.w
        ]
    
    def sketch(self) -> list[Point]:
        h, w = self.h, self.w
        a = Coord(0.0, 0.0)
        b = Coord(h, 0.0)
        c = Coord(h, w)
        d = Coord(0.0, w)
        a, b, c, d = random_rfss(a, b, c, d, scale=1)
        return [a, b, c, d]
    
    def draw(self):
        a, b, c, d = self.point2coord(self.a), self.point2coord(self.b), self.point2coord(self.c), self.point2coord(self.d)
        return [Segment(a, b), Segment(c, d), Segment(a, d), Segment(b, c)], []