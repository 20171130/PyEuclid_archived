from __future__ import annotations

import os
import pickle
import hashlib
import random
import matplotlib.patches as patches

from matplotlib import pyplot as plt
from itertools import product, zip_longest

import pyeuclid.formalization.utils as utils
from pyeuclid.formalization.relation import *
from pyeuclid.formalization.construction_rule import *
from pyeuclid.formalization.numericals import *
from pyeuclid.formalization.utils import *


def hash_constructions_list(constructions_list):
    s = ", ".join(str(c) for constructions in constructions_list for c in constructions)
    return hashlib.md5(s.encode('utf-8')).hexdigest()

def hash_coordinates_list(coordinates_list):
    s = ", ".join(f"{str(p)}:{x},{y}" for coordinates in coordinates_list if coordinates for (p, x, y) in coordinates)
    return hashlib.md5(s.encode('utf-8')).hexdigest()

def merge_hashes(*hashes):
    combined = "|".join(hashes)  # Delimiter to avoid accidental collisions
    return hashlib.md5(combined.encode('utf-8')).hexdigest()

class MaxAttemptsError(Exception):
    """Raised when the maximum number of allowed attempts is reached."""
    pass

class DistanceError(Exception):
    """Raised when sampled points are too close or far away."""
    pass

class SamplingError(Exception):
    """Raised when cannot construct the desired points."""
    pass


class NumericalCheckingError(Exception):
    """Raised when numerical checking fails."""
    pass


class Diagram:    
    def __new__(cls, constructions_list:list[list[ConstructionRule]]=[], coordinates_list=[], save_path=None, cache_folder=os.path.join(ROOT_DIR, 'cache'), resample=False):
        if cache_folder is not None:
            if not os.path.exists(cache_folder):
                os.makedirs(cache_folder)
        
        if not resample and cache_folder is not None:
            if constructions_list:
                h = hash_constructions_list(constructions_list)
                if coordinates_list:
                    h = merge_hashes(h, hash_coordinates_list(coordinates_list))
                file_name = f"{h}.pkl"
                file_path = os.path.join(cache_folder, file_name)
                try:
                    if os.path.exists(file_path):
                        with open(file_path, 'rb') as f:
                            instance = pickle.load(f)
                            instance.save_path = save_path
                            instance.save_diagram()
                            # print(f"Load existing diagram from {file_path}...")
                            return instance
                except :
                    pass
        
        instance = super().__new__(cls)
        return instance
    
    def __init__(self, constructions_list:list[list[ConstructionRule]]=[], coordinates_list=[], save_path=None, cache_folder=os.path.join(ROOT_DIR, 'cache'), resample=False):
        if hasattr(self, 'cache_folder'):
            return
    
        self.points = []
        self.segments = []
        self.circles = []
        self.highlight_angles = []
        self.highlight_segments = []
        
        self.name2point = {}
        self.point2name = {}
        
        self.construction2diagram = {}
        self.constructions_list = []
        self.coordinates_list = []
        self.auxiliary_constructions = []

        self.min_tol = 0.2
        self.max_tol = 2

        self.numerical_cache = {}
        
        self.fig, self.ax = None, None

        self.save_path = save_path
        self.cache_folder = cache_folder
        
        if constructions_list:                
            self.construct_diagram(constructions_list, coordinates_list)
            
    def clear(self):
        self.points.clear()
        self.segments.clear()
        self.circles.clear()
        self.highlight_segments.clear()
        self.highlight_angles.clear()
        self.name2point.clear()
        self.point2name.clear()
        self.auxiliary_constructions.clear()
        self.construction2diagram.clear()
        self.constructions_list.clear()
        self.numerical_cache.clear()
        self.coordinates_list.clear()
    
    def save(self):
        self._saved = {
            'points': self.points.copy(),
            'segments': self.segments.copy(),
            'circles': self.circles.copy(),
            'highlight_segments': self.highlight_segments.copy(),
            'highlight_angles': self.highlight_angles.copy(),
            'name2point': self.name2point.copy(),
            'point2name': self.point2name.copy(),
            'auxiliary_constructions': self.auxiliary_constructions.copy(),
            'construction2diagram': self.construction2diagram.copy(),
            'constructions_list': self.constructions_list.copy(),
            'coordinates_list': self.coordinates_list.copy(),
            'numerical_cache': self.numerical_cache.copy()
        }
    
    def restore(self):
        if hasattr(self, '_saved'):
            self.points = self._saved['points']
            self.segments = self._saved['segments']
            self.circles = self._saved['circles']
            self.highlight_segments = self._saved['highlight_segments']
            self.highlight_angles = self._saved['highlight_angles']
            self.name2point = self._saved['name2point']
            self.point2name = self._saved['point2name']
            self.auxiliary_constructions = self._saved['auxiliary_constructions']
            self.construction2diagram = self._saved['construction2diagram']
            self.constructions_list = self._saved['constructions_list']
            self.coordinates_list = self._saved['coordinates_list']
            self.numerical_cache = self._saved['numerical_cache']
        
    def show(self):
        self.draw_diagram(show=True)
        
    def save_to_cache(self):
        if self.cache_folder is not None:
            h = hash_constructions_list(self.constructions_list)
            if self.coordinates_list:
                h = merge_hashes(h, hash_coordinates_list(self.coordinates_list))
            file_name = f"{h}.pkl"
            file_path = os.path.join(self.cache_folder, file_name)
            # print(f'Save to {file_path}...')
            with open(file_path, 'wb') as f:
                pickle.dump(self, f)
    
    def add_constructions(self, constructions, coordinates=None, auxiliary=False):
        self.save()
        max_attempts = utils.MAX_DIAGRAM_ATTEMPTS or float('inf')
        attempt = 0

        while attempt < max_attempts:
            attempt += 1
            try:
                new_points = self.construct(constructions, coordinates)
                self.draw(new_points, constructions, auxiliary)
                self.constructions_list.append(constructions)
                if coordinates:
                    self.coordinates_list.append(coordinates)
                return
            except (NumericalCheckingError, SamplingError, DistanceError):
                self.restore()
            except Exception:
                raise                
        raise MaxAttemptsError()
            
    def construct_diagram(self, constructions_list, coordinates_list):
        max_attempts = utils.MAX_DIAGRAM_ATTEMPTS or float('inf')
        attempt = 0

        while attempt < max_attempts:
            attempt += 1
            try:
                self.clear()
                for constructions, coordinates in zip_longest(constructions_list, coordinates_list, fillvalue=None):
                    new_points = self.construct(constructions, coordinates)
                    self.draw(new_points, constructions, auxiliary=False)
                    self.constructions_list.append(constructions)
                    if coordinates:
                        self.coordinates_list.append(coordinates)
                self.draw_diagram()
                self.save_to_cache()
                return
            except (NumericalCheckingError, SamplingError, DistanceError):
                continue
            except Exception:
                raise
        
        raise MaxAttemptsError()
            
    def construct(self, constructions: list[ConstructionRule], coordinates=None):
        outputs = constructions[0].outputs
        if any(construction.outputs != outputs for construction in constructions[1:]):
            raise Exception()
        
        if coordinates:
            # given coordinates
            if [c[0] for c in coordinates] != outputs:
                raise Exception()
            new_points = [Point(c[1], c[2]) for c in coordinates]
        else:
            # sampling
            to_be_intersected = []
            for construction in constructions:
                for c in construction.conditions():
                    if not self.numerical_check(c):
                        raise NumericalCheckingError()
                to_be_intersected += self.sketch(construction)
            
            new_points = self.reduce(to_be_intersected, self.points)
            self.check_distance(new_points)

        self.points = self.points + new_points # Rebinds to a new list
        
        for p, np in zip(outputs, new_points):
            self.name2point[p.name] = np
            self.point2name[np] = p.name
        
        return new_points
    
    def check_distance(self, new_points):
        if not self.points or len(self.points) < 2:
            return
        
        if check_too_close(self.points, new_points, self.min_tol):
            self.min_tol = max(1e-2, self.min_tol - 0.01)
            raise DistanceError()
        
        if check_too_far(self.points, new_points, self.max_tol):
            self.max_tol = min(10, self.max_tol + 1)
            raise DistanceError()
            
    def numerical_check_goal(self, goal):
        if isinstance(goal, tuple):
            for g in goal:
                if self.numerical_check(g):
                    return True, g
        else:
            if self.numerical_check(goal):
                return True, goal
        return False, goal
            
    def numerical_check(self, relation):
        if isinstance(relation, Relation):
            # high-level relations
            if not 'check_' + relation.__class__.__name__.lower() in globals():
                return True
            func = globals()['check_' + relation.__class__.__name__.lower()]
            args = [self.name2point[p.name] for p in relation.get_points()]
            if relation not in self.numerical_cache:
                if relation.negated:
                    self.numerical_cache[relation] = not func(args)
                else:
                    self.numerical_cache[relation] = func(args)
            return self.numerical_cache[relation]
        else:
            if relation not in self.numerical_cache:
                symbol2value = {}
                symbols, symbol_names = parse_expression(relation)
                
                for angle_symbol, angle_name in zip(symbols['Angle'], symbol_names['Angle']):
                    angle_value = calculate_angle(*[self.name2point[n] for n in angle_name])
                    symbol2value[angle_symbol] = angle_value
                
                for length_symbol, length_name in zip(symbols['Length'], symbol_names['Length']):
                    length_value = calculate_length(*[self.name2point[n] for n in length_name])
                    symbol2value[length_symbol] = length_value
                
                evaluated_expr = relation.subs(symbol2value)
                self.numerical_cache[relation] = close_enough(float(evaluated_expr.evalf()), 0)
            
            return self.numerical_cache[relation]

    def sketch(self, construction):
        func = getattr(self, 'sketch_' + construction.__class__.__name__[10:])
        args = [arg if isinstance(arg, float) else self.name2point[arg.name] for arg in construction.inputs]
        result = func(*args)
        if isinstance(result, list):
            return result
        else:
            return [result]
        
    def sketch_angle_bisector(self, *args: list[Point]) -> Ray:
        a, b, c = args
        dist_ab = a.distance(b)
        dist_bc = b.distance(c)
        x = b + (c - b) * (dist_ab / dist_bc)
        m = (a + x) * 0.5
        return Ray(b, m)
    
    def sketch_angle_bisector2(self, *args: list[Point]) -> Ray:
        a, b, c = args
        dist_ab = a.distance(b)
        dist_bc = b.distance(c)
        x = b + (c - b) * (dist_ab / dist_bc)
        m = (a + x) * 0.5
        m_prime = Point(2*b.x - m.x, 2*b.y - m.y)
        return Ray(b, m_prime)
    
    def sketch_angle_mirror(self, *args: list[Point]) -> Ray:
        a, b, c = args
        ab = a - b
        cb = c - b

        dist_ab = a.distance(b)
        ang_ab = np.arctan2(ab.y / dist_ab, ab.x / dist_ab)
        dist_cb = c.distance(b)
        ang_bc = np.arctan2(cb.y / dist_cb, cb.x / dist_cb)

        ang_bx = 2 * ang_bc - ang_ab
        x = b + Point(np.cos(ang_bx), np.sin(ang_bx))
        return Ray(b, x)
    
    def sketch_circle(self, *args: list[Point]) -> Point:
        a, b, c = args
        l1 = perpendicular_bisector(a, b)
        l2 = perpendicular_bisector(b, c)
        x = intersect(l1, l2)
        return x
    
    def sketch_circumcenter(self, *args: list[Point]) -> Point:
        a, b, c = args
        l1 = perpendicular_bisector(a, b)
        l2 = perpendicular_bisector(b, c)
        x = intersect(l1, l2)
        return x
    
    def sketch_eq_quadrangle(self, *args: list[Point]) -> list[Point]:
        a = Point(0.0, 0.0)
        b = Point(1.0, 0.0)

        length = np.random.uniform(0.5, 2.0)
        ang = np.random.uniform(np.pi / 3, np.pi * 2 / 3)
        d = head_from(a, ang, length)

        ang = ang_of(b, d)
        ang = np.random.uniform(ang / 10, ang / 9)
        c = head_from(b, ang, length)
        a, b, c, d = random_rfss(a, b, c, d)
        return [a, b, c, d]
        
    def sketch_eq_trapezoid(self, *args: list[Point]) -> list[Point]:
        a = Point(0.0, 0.0)
        b = Point(1.0, 0.0)
        l = unif(0.5, 2.0)

        height = unif(0.5, 2.0)
        c = Point(0.5 + l / 2.0, height)
        d = Point(0.5 - l / 2.0, height)

        a, b, c, d = random_rfss(a, b, c, d)
        return [a, b, c, d]
    
    def sketch_eq_triangle(self, *args: list[Point]) -> list[Circle]:
        b, c = args
        return [Circle(center=b, radius=b.distance(c)), Circle(center=c, radius=b.distance(c))]
    
    def sketch_eqangle2(self, *args: list[Point]) -> Point:
        a, b, c = args
        
        ba = b.distance(a)
        bc = b.distance(c)
        l = ba * ba / bc

        if unif(0.0, 1.0) < 0.5:
            be = min(l, bc)
            be = unif(be * 0.1, be * 0.9)
        else:
            be = max(l, bc)
            be = unif(be * 1.1, be * 1.5)

        e = b + (c - b) * (be / bc)
        y = b + (a - b) * (be / l)
        return intersect(Line(c, y), Line(a, e))
    
    def sketch_eqdia_quadrangle(self, *args) -> list[Point]:
        m = unif(0.3, 0.7)
        n = unif(0.3, 0.7)
        a = Point(-m, 0.0)
        c = Point(1 - m, 0.0)
        b = Point(0.0, -n)
        d = Point(0.0, 1 - n)

        ang = unif(-0.25 * np.pi, 0.25 * np.pi)
        sin, cos = np.sin(ang), np.cos(ang)
        b = b.rotate(sin, cos)
        d = d.rotate(sin, cos)
        a, b, c, d = random_rfss(a, b, c, d)
        return [a, b, c, d]
        
    def sketch_eqdistance(self, *args) -> Circle:
        a, b, c = args
        return Circle(center=a, radius=b.distance(c))
    
    def sketch_eqdistance2(self, *args) -> Circle:
        a, b, c, alpha = args
        return Circle(center=a, radius=alpha*b.distance(c))
    
    def sketch_eqdistance3(self, *args) -> Circle:
        a, alpha = args
        return Circle(center=a, radius=alpha)
    
    def sketch_foot(self, *args) -> Point:
        a, b, c = args
        line_bc = Line(b, c)
        tline = a.perpendicular_line(line_bc)
        return intersect(tline, line_bc)
    
    def sketch_free(self, *args) -> Point:
        return Point(unif(-1, 1), unif(-1, 1))
    
    def sketch_incenter(self, *args) -> Point:
        a, b, c = args
        l1 = self.sketch_angle_bisector(a, b, c)
        l2 = self.sketch_angle_bisector(b, c, a)
        return intersect(l1, l2)
    
    def sketch_incenter2(self, *args) -> list[Point]:
        a, b, c = args
        i = self.sketch_incenter(a, b, c)
        x = i.foot(Line(b, c))
        y = i.foot(Line(c, a))
        z = i.foot(Line(a, b))
        return [x, y, z, i]
    
    def sketch_excenter(self, *args) -> Point:
        a, b, c = args
        l1 = self.sketch_angle_bisector(b, a, c)
        l2 = self.sketch_angle_bisector(a, b, c).line.perpendicular_line(b)
        return intersect(l1, l2)
    
    def sketch_excenter2(self, *args) -> list[Point]:
        a, b, c = args
        i = self.sketch_excenter(a, b, c)
        x = i.foot(Line(b, c))
        y = i.foot(Line(c, a))
        z = i.foot(Line(a, b))
        return [x, y, z, i]
    
    def sketch_centroid(self, *args) -> list[Point]:
        a, b, c = args
        x = (b + c) * 0.5
        y = (c + a) * 0.5
        z = (a + b) * 0.5
        i = intersect(Line(a, x), Line(b, y))
        return [x, y, z, i]
    
    def sketch_intersection_cc(self, *args) -> list[Circle]:
        o, w, a = args
        return [Circle(center=o, radius=o.distance(a)), Circle(center=w, radius=w.distance(a))]
    
    def sketch_intersection_lc(self, *args) -> list:
        a, o, b = args
        return [Line(b, a), Circle(center=o, radius=o.distance(b))]
    
    def sketch_intersection_ll(self, *args) -> Point:
        a, b, c, d = args
        l1 = Line(a, b)
        l2 = Line(c, d)
        return intersect(l1, l2)
    
    def sketch_intersection_lp(self, *args) -> Point:
        a, b, c, m, n = args
        l1 = Line(a,b)
        l2 = self.sketch_on_pline(c, m, n)
        return intersect(l1, l2)
    
    def sketch_intersection_lt(self, *args) -> Point:
        a, b, c, d, e = args
        l1 = Line(a, b)
        l2 = self.sketch_on_tline(c, d, e)
        return intersect(l1, l2)
    
    def sketch_intersection_pp(self, *args) -> Point:
        a, b, c, d, e, f = args
        l1 = self.sketch_on_pline(a, b, c)
        l2 = self.sketch_on_pline(d, e, f)
        return intersect(l1, l2)
    
    def sketch_intersection_tt(self, *args) -> Point:
        a, b, c, d, e, f = args
        l1 = self.sketch_on_tline(a, b, c)
        l2 = self.sketch_on_tline(d, e, f)
        return intersect(l1, l2)
    
    def sketch_iso_triangle(self, *args) -> list[Point]:
        base = unif(0.5, 1.5)
        height = unif(0.5, 1.5)

        b = Point(-base / 2, 0.0)
        c = Point(base / 2, 0.0)
        a = Point(0.0, height)
        a, b, c = random_rfss(a, b, c)
        return [a, b, c]
    
    def sketch_lc_tangent(self, *args) -> Line:
        a, o = args
        return self.sketch_on_tline(a, a, o)
    
    def sketch_midpoint(self, *args) -> Point:
        a, b = args
        return (a + b) * 0.5
    
    def sketch_mirror(self, *args) -> Point:
        a, b = args
        return b * 2 - a
    
    def sketch_nsquare(self, *args) -> Point:
        a, b = args
        ang = -np.pi / 2
        return a + (b - a).rotate(np.sin(ang), np.cos(ang))
    
    # def sketch_on_aline(self, *args) -> Ray:
    #     a, b, c, d, e = args
    #     '''
    #     x = xxx such that Angle(x, a, b) = Angle(c, d, e)
    #     return Ray(e, x)
    #     '''
    #     e, d, c, b, a = args
    #     ab = a - b
    #     cb = c - b
    #     de = d - e

    #     dab = a.distance(b)
    #     ang_ab = np.arctan2(ab.y / dab, ab.x / dab)

    #     dcb = c.distance(b)
    #     ang_bc = np.arctan2(cb.y / dcb, cb.x / dcb)

    #     dde = d.distance(e)
    #     ang_de = np.arctan2(de.y / dde, de.x / dde)

    #     ang_ex = ang_de + ang_bc - ang_ab
    #     x = e + Point(np.cos(ang_ex), np.sin(ang_ex))
    #     return Ray(e, x)

    def sketch_on_aline(self, *args) -> Ray:
        a, b, c, d, e = args

        # 1) compute the (unsigned) angle at d: ∠CDE in [0, π]
        ang_cde = calculate_angle(c, d, e)

        # 2) compute the baseline direction at a: angle of vector a→b
        dx_ab = b.x - a.x
        dy_ab = b.y - a.y
        ang_ab = np.arctan2(dy_ab, dx_ab)

        # 3) rotate the baseline by +ang_cde so that ∠XAB = ang_cde
        ang_ax1 = ang_ab + ang_cde
        ang_ax2 = ang_ab - ang_cde

        # 4) place x one unit from a along that direction
        x1 = Point(a.x + np.cos(ang_ax1), a.y + np.sin(ang_ax1))
        x2 = Point(a.x + np.cos(ang_ax2), a.y + np.sin(ang_ax2))

        assert close_enough(calculate_angle(b, a, x1), calculate_angle(c, d, e))
        assert close_enough(calculate_angle(b, a, x2), calculate_angle(c, d, e))

        return (Ray(a, x1), Ray(a, x2))
    
    def sketch_on_aline2(self, *args) -> Ray:
        a, b, c, d, e = args

        ang_cde = calculate_angle(c, d, e)
        dx_ab = b.x - a.x
        dy_ab = b.y - a.y
        ang_ab = np.arctan2(dy_ab, dx_ab)

        ang_ax1 = ang_ab + ang_cde
        ang_ax2 = ang_ab - ang_cde

        x1 = Point(a.x + np.cos(ang_ax1), a.y + np.sin(ang_ax1))
        x1_prime = Point(2*a.x - x1.x, 2*a.y - x1.y)
        
        x2 = Point(a.x + np.cos(ang_ax2), a.y + np.sin(ang_ax2))
        x2_prime = Point(2*a.x - x2.x, 2*a.y - x2.y)

        assert close_enough(calculate_angle(b, a, x1_prime) + calculate_angle(c, d, e), np.pi)
        assert close_enough(calculate_angle(b, a, x2_prime) + calculate_angle(c, d, e), np.pi)

        return (Ray(a, x1_prime), Ray(a, x2_prime))

    def sketch_on_bline(self, *args) -> Line:
        a, b = args
        m = (a + b) * 0.5
        return m.perpendicular_line(Line(a, b))
    
    def sketch_on_circle(self, *args) -> Circle:
        o, a = args
        return Circle(o, o.distance(a))
    
    def sketch_on_line(self, *args) -> Line:
        a, b = args
        return Line(a, b)
        
    def sketch_on_pline(self, *args) -> Line:
        a, b, c = args
        return a.parallel_line(Line(b, c))
    
    def sketch_on_tline(self, *args) -> Line:
        a, b, c = args
        return a.perpendicular_line(Line(b, c))
    
    def sketch_orthocenter(self, *args) -> Point:
        a, b, c = args
        l1 = self.sketch_on_tline(a, b, c)
        l2 = self.sketch_on_tline(b, c, a)
        return intersect(l1, l2)
    
    def sketch_parallelogram(self, *args) -> Point:
        a, b, c = args
        l1 = self.sketch_on_pline(a, b, c)
        l2 = self.sketch_on_pline(c, a, b)
        return intersect(l1, l2)
    
    def sketch_pentagon(self, *args) -> list[Point]:
        points = [Point(1.0, 0.0)]
        ang = 0.0

        for i in range(4):
            ang += (2 * np.pi - ang) / (5 - i) * unif(0.5, 1.5)
            point = Point(np.cos(ang), np.sin(ang))
            points.append(point)

        a, b, c, d, e = points  # pylint: disable=unbalanced-tuple-unpacking
        a, b, c, d, e = random_rfss(a, b, c, d, e)
        return [a, b, c, d, e]
    
    def sketch_psquare(self, *args) -> Point:
        a, b = args
        ang = np.pi / 2
        return a + (b - a).rotate(np.sin(ang), np.cos(ang))
    
    def sketch_quadrangle(self, *args) -> list[Point]:
        a = Point(0.0, 0.0)
        b = Point(1.0, 0.0)

        length = np.random.uniform(0.5, 2.0)
        ang = np.random.uniform(np.pi / 3, np.pi * 2 / 3)
        d = head_from(a, ang, length)

        ang = ang_of(b, d)
        ang = np.random.uniform(ang / 10, ang / 9)
        c = head_from(b, ang, length)
        a, b, c, d = random_rfss(a, b, c, d)
        return [a, b, c, d]
    
    def sketch_r_trapezoid(self, *args) -> list[Point]:
        a = Point(0.0, 1.0)
        d = Point(0.0, 0.0)
        b = Point(unif(0.5, 1.5), 1.0)
        c = Point(unif(0.5, 1.5), 0.0)
        a, b, c, d = random_rfss(a, b, c, d)
        return [a, b, c, d]
    
    def sketch_r_triangle(self, *args) -> list[Point]:
        a = Point(0.0, 0.0)
        b = Point(0.0, unif(0.5, 2.0))
        c = Point(unif(0.5, 2.0), 0.0)
        a, b, c = random_rfss(a, b, c)
        return [a, b, c]
    
    def sketch_rectangle(self, *args) -> list[Point]:
        a = Point(0.0, 0.0)
        b = Point(0.0, 1.0)
        l = unif(0.5, 2.0)
        c = Point(l, 1.0)
        d = Point(l, 0.0)
        a, b, c, d = random_rfss(a, b, c, d)
        return [a, b, c, d]
    
    def sketch_reflect(self, *args) -> Point:
        a, b, c = args
        m = a.foot(Line(b, c))
        return m * 2 - a
    
    def sketch_risos(self, *args) -> list[Point]:
        a = Point(0.0, 0.0)
        b = Point(0.0, 1.0)
        c = Point(1.0, 0.0)
        a, b, c = random_rfss(a, b, c)
        return [a, b, c]
    
    def sketch_s_angle(self, *args) -> Ray:
        a, b, alpha = args
        ang = alpha / 180 * np.pi
        x = b + (a - b).rotatea(ang)
        return Ray(b, x)
    
    def sketch_segment(self, *args) -> list[Point]:
        a = Point(unif(-1, 1), unif(-1, 1))
        b = Point(unif(-1, 1), unif(-1, 1))
        return [a, b]
    
    def sketch_shift(self, *args) -> Point:
        c, b, a = args
        return c + (b - a)
    
    def sketch_square(self, *args) -> list[Point]:
        a, b = args
        c = b + (a - b).rotatea(-np.pi / 2)
        d = a + (b - a).rotatea(np.pi / 2)
        return [c, d]
    
    def sketch_isquare(self, *args) -> list[Point]:
        a = Point(0.0, 0.0)
        b = Point(1.0, 0.0)
        c = Point(1.0, 1.0)
        d = Point(0.0, 1.0)
        a, b, c, d = random_rfss(a, b, c, d)
        return [a, b, c, d]
    
    def sketch_trapezoid(self, *args) -> list[Point]:
        d = Point(0.0, 0.0)
        c = Point(1.0, 0.0)

        base = unif(0.5, 2.0)
        height = unif(0.5, 2.0)
        a = Point(unif(0.2, 0.5), height)
        b = Point(a.x + base, height)
        a, b, c, d = random_rfss(a, b, c, d)
        return [a, b, c, d]
    
    def sketch_triangle(self, *args) -> list[Point]:
        a = Point(0.0, 0.0)
        b = Point(1.0, 0.0)
        ac = unif(0.5, 2.0)
        ang = unif(0.2, 0.8) * np.pi
        c = head_from(a, ang, ac)
        return [a, b, c]
    
    def sketch_triangle12(self, *args) -> list[Point]:
        b = Point(0.0, 0.0)
        c = Point(unif(1.5, 2.5), 0.0)
        a, _ = intersect(Circle(b, 1.0), Circle(c, 2.0))
        a, b, c = random_rfss(a, b, c)
        return [a, b, c]
    
    def sketch_2l1c(self, *args) -> list[Point]:
        a, b, c, p = args
        bc, ac = Line(b, c), Line(a, c)
        circle = Circle(p, p.distance(a))

        d, d_ = intersect(p.perpendicular_line(bc), circle)
        if bc.diff_side(d_, a):
            d = d_

        e, e_ = intersect(p.perpendicular_line(ac), circle)
        if ac.diff_side(e_, b):
            e = e_

        df = d.perpendicular_line(Line(p, d))
        ef = e.perpendicular_line(Line(p, e))
        f = intersect(df, ef)

        g, g_ = intersect(Line(c, f), circle)
        if bc.same_side(g_, a):
            g = g_

        b_ = c + (b - c) / b.distance(c)
        a_ = c + (a - c) / a.distance(c)
        m = (a_ + b_) * 0.5
        x = intersect(Line(c, m), Line(p, g))
        return [x.foot(ac), x.foot(bc), g, x]
    
    def sketch_e5128(self, *args) -> list[Point]:
        a, b, c, d = args
        g = (a + b) * 0.5
        de = Line(d, g)

        e, f = intersect(de, Circle(c, c.distance(b)))

        if e.distance(d) < f.distance(d):
            e = f
        return [e, g]
    
    def sketch_3peq(self, *args) -> list[Point]:
        a, b, c = args
        ab, bc, ca = Line(a, b), Line(b, c), Line(c, a)

        z = b + (c - b) * np.random.uniform(-0.5, 1.5)

        z_ = z * 2 - c
        l = z_.parallel_line(ca)
        x = intersect(l, ab)
        y = z * 2 - x
        return [x, y, z]
    
    def sketch_trisect(self, *args) -> list[Point]:
        a, b, c = args
        ang1 = ang_of(b, a)
        ang2 = ang_of(b, c)

        swap = 0
        if ang1 > ang2:
            ang1, ang2 = ang2, ang1
            swap += 1

        if ang2 - ang1 > np.pi:
            ang1, ang2 = ang2, ang1 + 2 * np.pi
            swap += 1

        angx = ang1 + (ang2 - ang1) / 3
        angy = ang2 - (ang2 - ang1) / 3

        x = b + Point(np.cos(angx), np.sin(angx))
        y = b + Point(np.cos(angy), np.sin(angy))

        ac = Line(a, c)
        x = intersect(Line(b, x), ac)
        y = intersect(Line(b, y), ac)

        if swap == 1:
            return [y, x]
        return [x, y]
    
    def sketch_trisegment(self, *args) -> list[Point]:
        a, b = args
        x, y = a + (b - a) * (1.0 / 3), a + (b - a) * (2.0 / 3)
        return [x, y]
    
    def sketch_on_dia(self, *args) -> Circle:
        a, b = args
        o = (a + b) * 0.5
        return Circle(o, o.distance(a))
    
    def sketch_ieq_triangle(self, *args) -> list[Point]:
        a = Point(0.0, 0.0)
        b = Point(1.0, 0.0)

        c, _ = intersect(Circle(a, a.distance(b)), Circle(b, b.distance(a)))
        return [a, b, c]
    
    def sketch_on_opline(self, *args) -> Ray:
        a, b = args
        return Ray(a, a + a - b)
    
    def sketch_cc_tangent(self, *args) -> list[Point]:
        o, a, w, b = args
        ra, rb = o.distance(a), w.distance(b)

        ow = Line(o, w)
        if close_enough(ra, rb):
            oo = ow.perpendicular_line(o)
            oa = Circle(o, ra)
            x, z = intersect(oo, oa)
            y = x + w - o
            t = z + w - o
            return [x, y, z, t]

        swap = rb > ra
        if swap:
            o, a, w, b = w, b, o, a
            ra, rb = rb, ra

        oa = Circle(o, ra)
        q = o + (w - o) * ra / (ra - rb)

        x, z = intersect(Circle(center=(o+q)*0.5, p1=o), oa)
        y = w.foot(Line(x, q))
        t = w.foot(Line(z, q))

        if swap:
            x, y, z, t = y, x, t, z

        return [x, y, z, t]

    
    def sketch_cc_tangent0(self, *args) -> Ray:
        o, a, w, b = args
        return self.sketch_cc_tangent(o, a, w, b)[:2]
    
    # TODO other side of x
    def sketch_eqangle3(self, *args) -> list[Point]:
        a, b, d, e, f = args
        de = d.distance(e)
        ef = e.distance(f)
        ab = b.distance(a)
        ang_ax = ang_of(a, b) + ang_between(e, d, f)
        x = head_from(a, ang_ax, length=de / ef * ab)
        o = self.sketch_circle(a, b, x)
        return [Circle(o, o.distance(a)), HalfPlane(o, a, b, opposingsides=calculate_angle(e,d,f)>pi/2)]
    
    def sketch_tangent(self, *args) -> list[Point]:
        a, o, b = args
        return list(intersect(Circle(o, o.distance(b)), Circle(center=(a+o)*0.5, p1=a)))
    
    def sketch_on_circum(self, *args) -> Circle:
        a, b, c = args
        o = self.sketch_circle(a, b, c)
        return Circle(o, o.distance(a))
    
    def sketch_sameside(self, *args) -> HalfPlane:
        a, b, c = args
        return HalfPlane(a, b, c)
    
    def sketch_opposingsides(self, *args) -> HalfPlane:
        a, b, c = args
        return HalfPlane(a, b, c, opposingsides=True)
    
    def reduce(self, objs: List[Any], existing_points) -> List[Point]:
        choices = []
        for obj in objs:
            if isinstance(obj, tuple):
                choices.append(obj)
            else:
                choices.append((obj,))
        
        for combo in product(*choices):
            try:
                new_points = self._reduce(list(combo), existing_points)
                return new_points
            except:
                continue
        raise SamplingError()
    
    def _reduce(self, objs, existing_points) -> list[Point]:
        essential_objs = [i for i in objs if not isinstance(i, HalfPlane)]
        halfplane_objs = [i for i in objs if isinstance(i, HalfPlane)]
  
        if all(isinstance(o, Point) for o in objs):
            return objs
        elif len(essential_objs) == 1:
            if not halfplane_objs:
                return objs[0].sample_within(existing_points)
            else:
                return objs[0].sample_within_halfplanes(existing_points,halfplane_objs)
  
        elif len(essential_objs) == 2:
            a, b = essential_objs
            result = intersect(a, b)
            if isinstance(result, Point):
                if halfplane_objs and not all(i.contains(result) for i in halfplane_objs):
                    raise SamplingError()
                return [result]
            
            a, b = result
            if halfplane_objs:
                a_correct_side = all(i.contains(a) for i in halfplane_objs)
                b_correct_side = all(i.contains(b) for i in halfplane_objs)
                
                if a_correct_side and not b_correct_side:
                    return [a]
                elif b_correct_side and not a_correct_side:
                    return [b]
                elif not a_correct_side and not b_correct_side:
                    raise SamplingError()
                        
            a_close = any([a.close(x) for x in existing_points])
            b_close = any([b.close(x) for x in existing_points])
            
            if a_close and b_close:
                raise SamplingError()
            elif a_close and not b_close:
                return [b]
            elif b_close and not a_close:
                return [a]
            else:
                return [np.random.choice([a, b])]
    
    def draw(self, new_points, constructions, auxiliary=False):
        for construction in constructions:
            len_s = len(self.segments)
            len_c = len(self.circles)
            len_hs = len(self.highlight_segments)
            len_ha = len(self.highlight_angles)
            func = getattr(self, 'draw_' + construction.__class__.__name__[10:])
            args = [arg if isinstance(arg, float) else self.name2point[arg.name] for arg in construction.inputs]
            func(*new_points, *args)
            self.construction2diagram[construction] = (
                new_points,
                self.segments[len_s:],
                self.circles[len_c:],
                self.highlight_segments[len_hs:],
                self.highlight_angles[len_ha:]
            )
            if auxiliary:
                self.auxiliary_constructions.append(construction)
            
    def draw_angle_bisector(self, *args):
        x, a, b, c = args
        self.segments.append(Segment(a, b))
        self.segments.append(Segment(b, c))
        self.segments.append(Segment(b, x))
        self.highlight_angles.append([[a, b, x], [x, b, c]])
    
    def draw_angle_bisector2(self, *args):
        x, a, b, c = args
        self.segments.append(Segment(a, b))
        self.segments.append(Segment(b, c))
        self.segments.append(Segment(b, x))
        self.highlight_angles.append([[a, b, x], [x, b, c]])
    
    def draw_angle_mirror(self, *args):
        x, a, b, c = args
        self.segments.append(Segment(a, b))
        self.segments.append(Segment(b, c))
        self.segments.append(Segment(b, x))
        self.highlight_angles.append([[a, b, c], [x, b, c]])
    
    def draw_circle(self, *args):
        x, a, b, c = args
        # self.segments.append(Segment(a, x))
        # self.segments.append(Segment(b, x))
        # self.segments.append(Segment(c, x))
        self.circles.append(Circle(x, x.distance(a)))
        
    def draw_circumcenter(self, *args):
        x, a, b, c = args
        # self.segments.append(Segment(a, x))
        # self.segments.append(Segment(b, x))
        # self.segments.append(Segment(c, x))
        self.circles.append(Circle(x, x.distance(a)))
        
    def draw_eq_quadrangle(self, *args):
        a, b, c, d = args
        self.segments.append(Segment(a, b))
        self.segments.append(Segment(b, c))
        self.segments.append(Segment(c, d))
        self.segments.append(Segment(d, a))
        self.highlight_segments.append([Segment(d, a), Segment(b, c)])
        
    def draw_eq_trapezoid(self, *args):
        a, b, c, d = args
        self.segments.append(Segment(a, b))
        self.segments.append(Segment(b, c))
        self.segments.append(Segment(c, d))
        self.segments.append(Segment(d, a))
        
    def draw_eq_triangle(self, *args):
        x, b, c = args
        self.segments.append(Segment(b, c))
        self.segments.append(Segment(c, x))
        self.segments.append(Segment(x, b))
    
    def draw_eqangle2(self, *args):
        x, a, b, c = args
        self.segments.append(Segment(b, a))
        self.segments.append(Segment(a, x))
        self.segments.append(Segment(c, b))
        self.segments.append(Segment(b, b))
    
    def draw_eqdia_quadrangle(self, *args):
        a, b, c, d = args
        self.segments.append(Segment(a, b))
        self.segments.append(Segment(b, c))
        self.segments.append(Segment(c, d))
        self.segments.append(Segment(d, a))
        self.segments.append(Segment(b, d))
        self.segments.append(Segment(a, c))
        self.highlight_segments.append([Segment(a, c), Segment(b, d)])
        
    def draw_eqdistance(self, *args):
        x, a, b, c = args
        self.segments.append(Segment(x, a))
        self.segments.append(Segment(b, c))
    
    def draw_eqdistance2(self, *args):
        x, a, b, c, alpha = args
        self.segments.append(Segment(x, a))
        self.segments.append(Segment(b, c))
        
    def draw_eqdistance2(self, *args):
        x, a, alpha = args
        self.segments.append(Segment(x, a))
    
    def draw_foot(self, *args):
        x, a, b, c = args
        self.segments.append(Segment(x, a))
        self.segments.append(Segment(x, b))
        self.segments.append(Segment(x, c))
        self.segments.append(Segment(b, c))
        self.highlight_angles.append([[a, x, np.random.choice([b, c])]])
    
    def draw_free(self, *args):
        x = args
        
    def draw_incenter(self, *args):
        i, a, b, c = args
        x = i.foot(Line(b, c))
        y = i.foot(Line(c, a))
        z = i.foot(Line(a, b))
        self.segments.append(Segment(a, b))
        self.segments.append(Segment(b, c))
        self.segments.append(Segment(c, a))
        self.circles.append(Circle(p1=x, p2=y, p3=z))
        
    def draw_incenter2(self, *args):
        x, y, z, i, a, b, c = args
        self.segments.append(Segment(a, b))
        self.segments.append(Segment(b, c))
        self.segments.append(Segment(c, a))
        self.circles.append(Circle(p1=x, p2=y, p3=z))
    
    def draw_excenter(self, *args):
        i, a, b, c = args
        x = i.foot(Line(b, c))
        y = i.foot(Line(c, a))
        z = i.foot(Line(a, b))
        self.segments.append(Segment(a, b))
        self.segments.append(Segment(b, c))
        self.segments.append(Segment(c, a))
        self.circles.append(Circle(p1=x, p2=y, p3=z))
        
    def draw_excenter2(self, *args):
        x, y, z, i, a, b, c = args
        self.segments.append(Segment(a, b))
        self.segments.append(Segment(b, c))
        self.segments.append(Segment(c, a))
        self.circles.append(Circle(p1=x, p2=y, p3=z))
        
    def draw_centroid(self, *args):
        x, y, z, i, a, b, c = args
        self.segments.append(Segment(a, b))
        self.segments.append(Segment(b, c))
        self.segments.append(Segment(c, a))
        self.segments.append(Segment(a, x))
        self.segments.append(Segment(b, y))
        self.segments.append(Segment(c, z))
    
    def draw_intersection_cc(self, *args):
        x, o, w, a = args
        self.segments.append(Segment(o, a))
        self.segments.append(Segment(o, x))
        self.segments.append(Segment(w, a))
        self.segments.append(Segment(w, x))
        self.circles.append(Circle(o, o.distance(a)))
        self.circles.append(Circle(w, w.distance(a)))
    
    def draw_intersection_lc(self, *args):
        x, a, o, b = args
        self.segments.append(Segment(x, a))
        self.segments.append(Segment(x, b))
        self.segments.append(Segment(a, b))
        self.segments.append(Segment(o, b))
        self.segments.append(Segment(o, x))
        self.circles.append(Circle(o, o.distance(b)))
        
    def draw_intersection_ll(self, *args):
        x, a, b, c, d = args
        self.segments.append(Segment(a, b))
        self.segments.append(Segment(c, d))
        self.segments.append(Segment(a, x))
        self.segments.append(Segment(b, x))
        self.segments.append(Segment(c, x))
        self.segments.append(Segment(d, x))
        
    def draw_intersection_lp(self, *args):
        x, a, b, c, m, n = args
        self.segments.append(Segment(a, b))
        self.segments.append(Segment(m, n))
        self.segments.append(Segment(a, x))
        self.segments.append(Segment(b, x))
        self.segments.append(Segment(c, x))
        
    def draw_intersection_lp(self, *args):
        x, a, b, c, m, n = args
        self.segments.append(Segment(a, b))
        self.segments.append(Segment(m, n))
        self.segments.append(Segment(a, x))
        self.segments.append(Segment(b, x))
        self.segments.append(Segment(c, x))
        
    def draw_intersection_lt(self, *args):
        x, a, b, c, d, e = args
        self.segments.append(Segment(a, b))
        self.segments.append(Segment(d, e))
        self.segments.append(Segment(a, x))
        self.segments.append(Segment(b, x))
        self.segments.append(Segment(c, x))
        
    def draw_intersection_pp(self, *args):
        x, a, b, c, d, e, f = args
        self.segments.append(Segment(a, x))
        self.segments.append(Segment(b, c))
        self.segments.append(Segment(d, x))
        self.segments.append(Segment(e, f))
    
    def draw_intersection_tt(self, *args):
        x, a, b, c, d, e, f = args
        self.segments.append(Segment(a, x))
        self.segments.append(Segment(b, c))
        self.segments.append(Segment(d, x))
        self.segments.append(Segment(e, f))
    
    def draw_iso_triangle(self, *args):
        a, b, c = args
        self.segments.append(Segment(a, b))
        self.segments.append(Segment(b, c))
        self.segments.append(Segment(c, a))
        
    def draw_lc_tangent(self, *args):
        x, a, o = args
        self.segments.append(Segment(a, x))
        self.segments.append(Segment(a, o))
        self.circles.append(Circle(o, o.distance(a)))
    
    def draw_midpoint(self, *args):
        x, a, b = args
        self.segments.append(Segment(a, x))
        self.segments.append(Segment(b, x))
    
    def draw_mirror(self, *args):
        x, a, b = args
        self.segments.append(Segment(a, b))
        self.segments.append(Segment(b, x))
        
    def draw_nsquare(self, *args):
        x, a, b = args
        self.segments.append(Segment(x, a))
        self.segments.append(Segment(a, b))
        self.segments.append(Segment(b, x))
    
    def draw_on_aline(self, *args):
        x, a, b, c, d, e = args
        self.segments.append(Segment(e, d))
        self.segments.append(Segment(d, c))
        self.segments.append(Segment(b, a))
        self.segments.append(Segment(a, x))
        self.highlight_angles.append([[x, a, b], [c, d, e]])
    
    def draw_on_aline2(self, *args):
        x, a, b, c, d, e = args
        self.segments.append(Segment(e, d))
        self.segments.append(Segment(d, c))
        self.segments.append(Segment(b, a))
        self.segments.append(Segment(a, x))
        self.highlight_angles.append([[x, a, b], [c, d, e]])
    
    def draw_on_bline(self, *args):
        x, a, b = args
        self.segments.append(Segment(a, b))
        self.segments.append(Segment(a, x))
        self.segments.append(Segment(b, x))
    
    def draw_on_circle(self, *args):
        x, o, a = args
        self.segments.append(Segment(o, a))
        self.segments.append(Segment(o, x))
        self.circles.append(Circle(o, o.distance(x)))
        
    def draw_on_line(self, *args):
        x, a, b = args
        self.segments.append(Segment(x, a))
        self.segments.append(Segment(x, b))
        self.segments.append(Segment(a, b))
        
    def draw_on_pline(self, *args):
        x, a, b, c = args
        self.segments.append(Segment(x, a))
        self.segments.append(Segment(b, c))
    
    def draw_on_tline(self, *args):
        x, a, b, c = args
        self.segments.append(Segment(x, a))
        self.segments.append(Segment(b, c))
    
    def draw_orthocenter(self, *args):
        x, a, b, c = args
        self.segments.append(Segment(a, b))
        self.segments.append(Segment(b, c))
        self.segments.append(Segment(c, a))
    
    def draw_parallelogram(self, *args):
        x, a, b, c = args
        self.segments.append(Segment(x, a))
        self.segments.append(Segment(a, b))
        self.segments.append(Segment(b, c))
        self.segments.append(Segment(c, x))
    
    def draw_parallelogram(self, *args):
        x, a, b, c = args
        self.segments.append(Segment(x, a))
        self.segments.append(Segment(a, b))
        self.segments.append(Segment(b, c))
        self.segments.append(Segment(c, x))
    
    def draw_pentagon(self, *args):
        a, b, c, d, e = args
        self.segments.append(Segment(a, b))
        self.segments.append(Segment(b, c))
        self.segments.append(Segment(c, d))
        self.segments.append(Segment(d, e))
        self.segments.append(Segment(e, a))
    
    def draw_psquare(self, *args):
        x, a, b = args
        self.segments.append(Segment(x, a))
        self.segments.append(Segment(a, b))
        
    def draw_quadrangle(self, *args):
        a, b, c, d = args
        self.segments.append(Segment(a, b))
        self.segments.append(Segment(b, c))
        self.segments.append(Segment(c, d))
        self.segments.append(Segment(d, a))
    
    def draw_r_trapezoid(self, *args):
        a, b, c, d = args
        self.segments.append(Segment(a, b))
        self.segments.append(Segment(b, c))
        self.segments.append(Segment(c, d))
        self.segments.append(Segment(d, a))
        self.highlight_angles.append([random.choice([[b, a, d], [a, d, c]])])
    
    def draw_r_triangle(self, *args):
        a, b, c = args
        self.segments.append(Segment(a, b))
        self.segments.append(Segment(b, c))
        self.segments.append(Segment(c, a))
        self.highlight_angles.append([[b, a, c]])
        
    def draw_rectangle(self, *args):
        a, b, c, d = args
        self.segments.append(Segment(a, b))
        self.segments.append(Segment(b, c))
        self.segments.append(Segment(c, d))
        self.segments.append(Segment(d, a))
    
    def draw_reflect(self, *args):
        x, a, b, c = args
        self.segments.append(Segment(b, c))
    
    def draw_risos(self, *args):
        a, b, c = args
        self.segments.append(Segment(a, b))
        self.segments.append(Segment(b, c))
        self.segments.append(Segment(c, a))
        self.highlight_angles.append([[b, a, c]])
    
    def draw_s_angle(self, *args):
        x, a, b, alpha = args
        self.segments.append(Segment(a, b))
        self.segments.append(Segment(b, x))
    
    def draw_segment(self, *args):
        a, b = args
        self.segments.append(Segment(a, b))
    
    def draw_s_segment(self, *args):
        a, b, alpha = args
        self.segments.append(Segment(a, b))
        
    def draw_shift(self, *args):
        x, b, c, d = args
        self.segments.append(Segment(x, b))
        self.segments.append(Segment(c, d))
        self.segments.append(Segment(x, c))
        self.segments.append(Segment(b, d))
    
    def draw_square(self, *args):
        x, y, a, b = args
        self.segments.append(Segment(a, b))
        self.segments.append(Segment(b, x))
        self.segments.append(Segment(x, y))
        self.segments.append(Segment(y, a))
    
    def draw_isquare(self, *args):
        a, b, c, d = args
        self.segments.append(Segment(a, b))
        self.segments.append(Segment(b, c))
        self.segments.append(Segment(c, d))
        self.segments.append(Segment(d, a))
    
    def draw_trapezoid(self, *args):
        a, b, c, d = args
        self.segments.append(Segment(a, b))
        self.segments.append(Segment(b, c))
        self.segments.append(Segment(c, d))
        self.segments.append(Segment(d, a))
    
    def draw_triangle(self, *args):
        a, b, c = args
        self.segments.append(Segment(a, b))
        self.segments.append(Segment(b, c))
        self.segments.append(Segment(c, a))
    
    def draw_triangle12(self, *args):
        a, b, c = args
        self.segments.append(Segment(a, b))
        self.segments.append(Segment(b, c))
        self.segments.append(Segment(c, a))
    
    def draw_2l1c(self, *args):
        x, y, z, i, a, b, c, o = args
        self.segments.append(Segment(a, c))
        self.segments.append(Segment(b, c))
        self.segments.append(Segment(a, o))
        self.segments.append(Segment(b, o))
        
        self.segments.append(Segment(i, x))
        self.segments.append(Segment(i, y))
        self.segments.append(Segment(i, z))
        
        self.segments.append(Segment(c, x))
        self.segments.append(Segment(a, x))
        self.segments.append(Segment(c, y))
        self.segments.append(Segment(b, y))
        self.segments.append(Segment(o, z))
        
        self.circles.append(Circle(i, i.distance(x)))
        self.circles.append(Circle(o, o.distance(a)))
    
    def draw_e5128(self, *args):
        x, y, a, b, c, d = args
        self.segments.append(Segment(a, b))
        self.segments.append(Segment(b, c))
        self.segments.append(Segment(c, d))
        self.segments.append(Segment(d, a))
        
        self.segments.append(Segment(a, x))
        self.segments.append(Segment(x, y))
        self.segments.append(Segment(c, x))
    
    def draw_3peq(self, *args):
        x, y, z, a, b, c = args
        self.segments.append(Segment(a, b))
        self.segments.append(Segment(b, c))
        self.segments.append(Segment(c, a))
        
        self.segments.append(Segment(a, x))
        self.segments.append(Segment(b, x))
        
        self.segments.append(Segment(a, y))
        self.segments.append(Segment(c, y))
        
        self.segments.append(Segment(c, z))
        self.segments.append(Segment(b, z))
        
        self.segments.append(Segment(x, y))
        self.segments.append(Segment(y, z))
        self.segments.append(Segment(z, x))
    
    def draw_trisect(self, *args):
        x, y, a, b, c = args
        self.segments.append(Segment(a, b))
        self.segments.append(Segment(b, c))
        
        self.segments.append(Segment(b, x))
        self.segments.append(Segment(b, y))
        
        self.segments.append(Segment(a, x))
        self.segments.append(Segment(x, y))
        self.segments.append(Segment(y, c))
        
    def draw_trisegment(self, *args):
        x, y, a, b = args
        self.segments.append(Segment(a, x))
        self.segments.append(Segment(x, y))
        self.segments.append(Segment(y, b))
    
    def draw_on_dia(self, *args):
        x, a, b = args
        self.segments.append(Segment(x, a))
        self.segments.append(Segment(x, b))
        self.highlight_angles.append([[a, x, b]])
        
    def draw_ieq_triangle(self, *args):
        a, b, c = args
        self.segments.append(Segment(a, b))
        self.segments.append(Segment(b, c))
        self.segments.append(Segment(c, a))
    
    def draw_on_opline(self, *args):
        x, a, b = args
        self.segments.append(Segment(a, b))
        self.segments.append(Segment(x, a))
        self.segments.append(Segment(x, b))
    
    def draw_cc_tangent0(self, *args):
        x, y, o, a, w, b = args
        self.segments.append(Segment(o, a))
        self.segments.append(Segment(o, x))
        
        self.segments.append(Segment(w, b))
        self.segments.append(Segment(w, y))
        
        self.segments.append(Segment(x, y))
        
        self.circles.append(Circle(o, o.distance(a)))
        self.circles.append(Circle(w, w.distance(b)))
    
    def draw_cc_tangent(self, *args):
        x, y, z, i, o, a, w, b = args
        self.segments.append(Segment(o, a))
        self.segments.append(Segment(o, x))
        self.segments.append(Segment(o, z))
        
        self.segments.append(Segment(w, b))
        self.segments.append(Segment(w, y))
        self.segments.append(Segment(w, i))
        
        self.segments.append(Segment(x, y))
        self.segments.append(Segment(z, i))
        
        self.circles.append(Circle(o, o.distance(a)))
        self.circles.append(Circle(w, w.distance(b)))
    
    def draw_eqangle3(self, *args):
        x, a, b, d, e, f = args
        self.segments.append(Segment(f, d))
        self.segments.append(Segment(d, e))
        
        self.segments.append(Segment(a, x))
        self.segments.append(Segment(x, b))
        self.highlight_angles.append([[a, x, b], [e, d, f]])
    
    def draw_tangent(self, *args):
        x, y, a, o, b = args
        self.segments.append(Segment(o, b))
        self.segments.append(Segment(o, x))
        self.segments.append(Segment(o, y))
        self.segments.append(Segment(a, x))
        self.segments.append(Segment(a, y))
        
        self.circles.append(Circle(o, o.distance(b)))
    
    def draw_on_circum(self, *args):
        x, a, b, c = args
        self.circles.append(Circle(p1=a, p2=b, p3=c))

    def draw_connect(self, *args):
        a, b = args
        self.segments.append(Segment(a, b))
    
    def draw_sameside(self, *args):
        x, a, b, c = args
    
    def draw_opposingsides(self, *args):
        x, a, b, c = args
    
    def draw_diagram(self, constructions=None, show=False, save=True):
        imsize = 512 / 100
        self.fig, self.ax = plt.subplots(figsize=(imsize, imsize), dpi=300)
        self.ax.set_facecolor((1.0, 1.0, 1.0))
        
        if constructions is None:
            constructions = [c for constructions in self.constructions_list for c in constructions]

        points = set()
        segments = set()
        circles = set()
        required_points = set()
        highlight_segments = []
        highlight_angles = []
        
        for construction in constructions:
            new_points, new_segments, new_circles, new_highlight_segments, new_highlight_angles = self.construction2diagram[construction]
            required_points.update(set(self.name2point[p.name] for p in construction.inputs if not isinstance(p, float)))
            points.update(new_points)
            segments.update(new_segments)
            circles.update(new_circles)
            highlight_segments.extend(new_highlight_segments)
            highlight_angles.extend(new_highlight_angles)

            for point in new_points:
                self.ax.scatter(point.x, point.y, color='black', s=15)

            for segment in new_segments:
                p1, p2 = segment.p1, segment.p2
                lx, ly = (p1.x, p2.x), (p1.y, p2.y)
                self.ax.plot(lx, ly, color='black', lw=1.2, alpha=0.8, 
                             ls='-' if construction not in self.auxiliary_constructions else '--')
                
            for circle in new_circles:
                self.ax.add_patch(
                    plt.Circle(
                        (circle.center.x, circle.center.y),
                        circle.radius,
                        color='red',
                        alpha=0.8,
                        fill=False,
                        lw=1.2,
                        ls='-' if construction not in self.auxiliary_constructions else '--'
                    )
                )
        
        for p in required_points:
            if p not in points:
                points.add(p)
        
        xmin = min([p.x for p in points])
        xmax = max([p.x for p in points])
        ymin = min([p.y for p in points])
        ymax = max([p.y for p in points])

        for c in circles:
            r = c.radius
            cx, cy = c.center.x, c.center.y
            xmin = min(xmin, cx - r)
            xmax = max(xmax, cx + r)
            ymin = min(ymin, cy - r)
            ymax = max(ymax, cy + r)

        xspan = xmax - xmin
        yspan = ymax - ymin
        span = max(xspan, yspan)
        
        for segments in new_highlight_segments:
            for segment in segments:
                p1, p2 = segment.p1, segment.p2
                ang = ang_of(p1, p2)
                leaned_ang = ang + np.pi / 2 + np.pi / 12
                mid = Point((p1.x + p2.x) / 2, (p1.y + p2.y) / 2)
                start = head_from(mid, leaned_ang + np.pi, span / 60)
                end = head_from(mid, leaned_ang, span / 60)
                self.ax.plot([start.x, end.x], [start.y, end.y], color='black', lw=1.2, alpha=0.8, ls='-')

        for angles in highlight_angles:
            if len(angles) == 1:
                a, b, c = angles[0]
                assert close_enough(calculate_angle(a, b, c), np.pi/2)
                v1 = (a - b) / a.distance(b)
                v2 = (c - b) / c.distance(b)
                p1 = b + v1 * span / 30
                p2 = p1 + v2 * span / 30
                p3 = b + v2 * span / 30
                self.ax.plot([p1.x, p2.x], [p1.y, p2.y], color='black', lw=1.2, alpha=0.8, ls='-')
                self.ax.plot([p2.x, p3.x], [p2.y, p3.y], color='black', lw=1.2, alpha=0.8, ls='-')
                segments.add(Segment(p1, p2))
                segments.add(Segment(p2, p3))
            else:
                for angle in angles:
                    a, b, c = angle
                    angle_ba = ang_of(b, a) * 180 / np.pi
                    angle_bc = ang_of(b, c) * 180 / np.pi
                    
                    diff = (angle_bc - angle_ba) % 360
                    
                    if diff <= 180:
                        theta1 = angle_ba
                        sweep = diff
                    else:
                        theta1 = angle_bc
                        sweep = 360 - diff
                    
                    self.ax.add_patch(
                        patches.Arc(
                            (b.x, b.y), span / 10, span / 10,
                            angle=0,
                            theta1=theta1,
                            theta2=theta1 + sweep,
                            color='black', lw=1.2, alpha=0.8
                        )
                    )

        def annotation_position(p):
            r = span / 20
            c = Circle(p, r)
            avoids = []
            for segment in segments:
                try:
                    avoids.extend(circle_segment_intersection(c, segment))
                except:
                    continue
            
            for circle in circles:
                try:
                    avoids.extend(intersect(c, circle))
                except:
                    continue
            
            if not avoids:
                return p.x + r / np.sqrt(2), p.y + r / np.sqrt(2)
            
            angs = sorted([ang_of(p, a) for a in avoids])
            angs += [angs[0] + 2 * np.pi]
            angs = [(angs[i + 1] - a, a) for i, a in enumerate(angs[:-1])]
            
            d, a = max(angs)
            ang = a + d / 2
            
            point_position = p + Point(np.cos(ang), np.sin(ang)) * r
            return point_position.x, point_position.y
            
        for p in points:
            x_pos, y_pos = annotation_position(p)
            
            xmax = max(xmax, x_pos)
            xmin = min(xmin, x_pos)
            ymax = max(ymax, y_pos)
            ymin = min(ymin, y_pos)
            
            self.ax.annotate(self.point2name[p].upper(), (x_pos, y_pos), color='black', ha='center', va='center', fontsize=12)
        
        self.ax.set_aspect('equal')
        self.ax.set_axis_off()
        
        x_margin = (xmax - xmin) * 0.1
        y_margin = (ymax - ymin) * 0.1

        self.ax.set_xlim(xmin - x_margin, xmax + x_margin)
        self.ax.set_ylim(ymin - y_margin, ymax + y_margin)
        
        if save:
            # print(f'Save diagram to {self.save_path}...')
            self.save_diagram()
        
        if show:
            plt.show()
            
        plt.close(self.fig)
    
    def save_diagram(self):
        if self.save_path is not None:
            parent_dir = os.path.dirname(self.save_path)
            if parent_dir and not os.path.exists(parent_dir):
                os.makedirs(parent_dir)
            self.fig.savefig(self.save_path)

        