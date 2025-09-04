from sympy import pi
import random
from .construction_rule import *
from .diagram import random_rfss, Circle, Segment, Ray
from .diagram import Point as Coord
import numpy as np
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
        x1 = Coord(a.x + np.cos(ang_ax1), a.y + np.sin(ang_ax1))

        return Ray(a, x1)
    
    
    def draw(self):
        return [Segment(self.point2coord(self.a), self.point2coord(self.x)), Segment(self.point2coord(self.a), self.point2coord(self.b))], []
        
    
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
        x1 = Coord(a.x + np.cos(ang_ax1), a.y + np.sin(ang_ax1))

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
        return [], [Circle(self.point2coord(self.o), self.r)]

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
        return [Segment(self.point2coord(self.a), self.point2coord(self.x))], []

# triangles can be constructed with construct_angle_q and construct_on_circle
# @register("independent")
# class construct_triangle_asa(ConstructionQ):
#     def construct(self, a: Point, b: Point, c: Point):
#         self.outputs = [a, b, c]
#         self.abc = saf.bc], [self.abc, self.bca]
    
#     def conclusionmple_angle()
#         self.bca = sample_angle(high = pi-self.bca)
#         self.bc = sample_length()
#         return [sels(self):
#         a, b, c = self.outputs
#         return [
#             Triangle(a, b, c),
#             Angle(a, b, c) - self.abc,
#             Angle(b, c, a) - self.bca,
#             Length(b, c) - self.bc
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