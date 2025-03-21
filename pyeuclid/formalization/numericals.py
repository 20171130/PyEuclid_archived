from __future__ import annotations
from typing import Any, Optional, Union

import numpy as np


ATOM = 1e-4


class NumerialCheckFailError(Exception):
  pass


class Point:
  def __init__(self, x, y):
    self.x = x
    self.y = y

  def __lt__(self, other: Point) -> bool:
    return (self.x, self.y) < (other.x, other.y)

  def __gt__(self, other: Point) -> bool:
    return (self.x, self.y) > (other.x, other.y)

  def __add__(self, p: Point) -> Point:
    return Point(self.x + p.x, self.y + p.y)

  def __sub__(self, p: Point) -> Point:
    return Point(self.x - p.x, self.y - p.y)

  def __mul__(self, f: float) -> Point:
    return Point(self.x * f, self.y * f)

  def __rmul__(self, f: float) -> Point:
    return self * f

  def __truediv__(self, f: float) -> Point:
    return Point(self.x / f, self.y / f)

  def __floordiv__(self, f: float) -> Point:
    div = self / f  # true div
    return Point(int(div.x), int(div.y))

  def __str__(self) -> str:
    return 'P({},{})'.format(self.x, self.y)

  def close(self, point: Point, tol: float = 1e-12) -> bool:
    return abs(self.x - point.x) < tol and abs(self.y - point.y) < tol

  def midpoint(self, p: Point) -> Point:
    return Point(0.5 * (self.x + p.x), 0.5 * (self.y + p.y))

  def distance(self, p: Union[Point, Line, Circle]) -> float:
    if isinstance(p, Line):
      return p.distance(self)
    if isinstance(p, Circle):
      return abs(p.radius - self.distance(p.center))
    dx = self.x - p.x
    dy = self.y - p.y
    return np.sqrt(dx * dx + dy * dy)

  def distance2(self, p: Point) -> float:
    if isinstance(p, Line):
      return p.distance(self)
    dx = self.x - p.x
    dy = self.y - p.y
    return dx * dx + dy * dy

  def rotatea(self, ang: float) -> Point:
    sinb, cosb = np.sin(ang), np.cos(ang)
    return self.rotate(sinb, cosb)

  def rotate(self, sinb: float, cosb: float) -> Point:
    x, y = self.x, self.y
    return Point(x * cosb - y * sinb, x * sinb + y * cosb)

  def flip(self) -> Point:
    return Point(-self.x, self.y)

  def perpendicular_line(self, line: Line) -> Line:
    return line.perpendicular_line(self)

  def foot(self, line: Line) -> Point:
    if isinstance(line, Line):
      l = line.perpendicular_line(self)
      return line_line_intersection(l, line)
    elif isinstance(line, Circle):
      c, r = line.center, line.radius
      return c + (self - c) * r / self.distance(c)
    raise ValueError('Dropping foot to weird type {}'.format(type(line)))

  def parallel_line(self, line: Line) -> Line:
    return line.parallel_line(self)

  def norm(self) -> float:
    return np.sqrt(self.x**2 + self.y**2)

  def cos(self, other: Point) -> float:
    x, y = self.x, self.y
    a, b = other.x, other.y
    return (x * a + y * b) / self.norm() / other.norm()

  def dot(self, other: Point) -> float:
    return self.x * other.x + self.y * other.y

  def sign(self, line: Line) -> int:
    return line.sign(self)

  def is_same(self, other: Point) -> bool:
    return self.distance(other) <= ATOM

class Line:
  def __init__(
      self,
      p1: Point = None,
      p2: Point = None,
      coefficients: tuple[int, int, int] = None,
  ):
    if p1 is None and p2 is None and coefficients is None:
      self.coefficients = None, None, None
      return

    a, b, c = coefficients or (
        p1.y - p2.y,
        p2.x - p1.x,
        p1.x * p2.y - p2.x * p1.y,
    )

    # Make sure a is always positive (or always negative for that matter)
    # With a == 0, Assuming a = +epsilon > 0
    # Then b such that ax + by = 0 with y>0 should be negative.
    if a < 0.0 or a == 0.0 and b > 0.0:
      a, b, c = -a, -b, -c

    self.coefficients = a, b, c

  def parallel_line(self, p: Point) -> Line:
    a, b, _ = self.coefficients
    return Line(coefficients=(a, b, -a * p.x - b * p.y))  # pylint: disable=invalid-unary-operand-type

  def perpendicular_line(self, p: Point) -> Line:
    a, b, _ = self.coefficients
    return Line(p, p + Point(a, b))

  def greater_than(self, other: Line) -> bool:
    a, b, _ = self.coefficients
    x, y, _ = other.coefficients
    # b/a > y/x
    return b * x > a * y

  def __gt__(self, other: Line) -> bool:
    return self.greater_than(other)

  def __lt__(self, other: Line) -> bool:
    return other.greater_than(self)

  def same(self, other: Line) -> bool:
    a, b, c = self.coefficients
    x, y, z = other.coefficients
    return close_enough(a * y, b * x) and close_enough(b * z, c * y)

  def equal(self, other: Line) -> bool:
    a, b, _ = self.coefficients
    x, y, _ = other.coefficients
    # b/a == y/x
    return b * x == a * y

  def less_than(self, other: Line) -> bool:
    a, b, _ = self.coefficients
    x, y, _ = other.coefficients
    # b/a > y/x
    return b * x < a * y

  def intersect(self, obj: Union[Line, Circle]) -> tuple[Point, ...]:
    if isinstance(obj, Line):
      return line_line_intersection(self, obj)
    if isinstance(obj, Circle):
      return line_circle_intersection(self, obj)

  def distance(self, p: Point) -> float:
    a, b, c = self.coefficients
    return abs(self(p.x, p.y)) / math.sqrt(a * a + b * b)

  def __call__(self, x: Point, y: Point = None) -> float:
    if isinstance(x, Point) and y is None:
      return self(x.x, x.y)
    a, b, c = self.coefficients
    return x * a + y * b + c

  def is_parallel(self, other: Line) -> bool:
    a, b, _ = self.coefficients
    x, y, _ = other.coefficients
    return abs(a * y - b * x) < ATOM

  def is_perp(self, other: Line) -> bool:
    a, b, _ = self.coefficients
    x, y, _ = other.coefficients
    return abs(a * x + b * y) < ATOM

  def cross(self, other: Line) -> float:
    a, b, _ = self.coefficients
    x, y, _ = other.coefficients
    return a * y - b * x

  def dot(self, other: Line) -> float:
    a, b, _ = self.coefficients
    x, y, _ = other.coefficients
    return a * x + b * y

  def point_at(self, x: float = None, y: float = None) -> Optional[Point]:
    """Get a point on line closest to (x, y)."""
    a, b, c = self.coefficients
    # ax + by + c = 0
    if x is None and y is not None:
      if a != 0:
        return Point((-c - b * y) / a, y)  # pylint: disable=invalid-unary-operand-type
      else:
        return None
    elif x is not None and y is None:
      if b != 0:
        return Point(x, (-c - a * x) / b)  # pylint: disable=invalid-unary-operand-type
      else:
        return None
    elif x is not None and y is not None:
      if a * x + b * y + c == 0.0:
        return Point(x, y)
    return None

  # def diff_side(self, p1: Point, p2: Point) -> Optional[bool]:
  #   d1 = self(p1.x, p1.y)
  #   d2 = self(p2.x, p2.y)
  #   if d1 == 0 or d2 == 0:
  #     return None
  #   return d1 * d2 < 0

  # def same_side(self, p1: Point, p2: Point) -> Optional[bool]:
  #   d1 = self(p1.x, p1.y)
  #   d2 = self(p2.x, p2.y)
  #   if d1 == 0 or d2 == 0:
  #     return None
  #   return d1 * d2 > 0
  
  def diff_side(self, p1: Point, p2: Point) -> Optional[bool]:
    d1 = self(p1.x, p1.y)
    d2 = self(p2.x, p2.y)
    if abs(d1) < ATOM or abs(d2) < ATOM:
      return None
    return d1 * d2 < 0

  def same_side(self, p1: Point, p2: Point) -> Optional[bool]:
    d1 = self(p1.x, p1.y)
    d2 = self(p2.x, p2.y)
    if abs(d1) < ATOM or abs(d2) < ATOM:
      return None
    return d1 * d2 > 0

  def sign(self, point: Point) -> int:
    s = self(point.x, point.y)
    if s > 0:
      return 1
    elif s < 0:
      return -1
    return 0

  def is_same(self, other: Line) -> bool:
    a, b, c = self.coefficients
    x, y, z = other.coefficients
    return abs(a * y - b * x) <= ATOM and abs(b * z - c * y) <= ATOM

  def sample_within(self, points: list[Point], n: int = 5) -> list[Point]:
    """Sample a point within the boundary of points."""
    center = sum(points, Point(0.0, 0.0)) * (1.0 / len(points))
    radius = max([p.distance(center) for p in points])
    if close_enough(center.distance(self), radius):
      center = center.foot(self)
    a, b = line_circle_intersection(self, Circle(center.foot(self), radius))

    result = None
    best = -1.0
    for _ in range(n):
      rand = unif(0.0, 1.0)
      x = a + (b - a) * rand
      mind = min([x.distance(p) for p in points])
      if mind > best:
        best = mind
        result = x
    return [result]
  
  def sample_within_halfplanes(self, points: list[Point], halfplanes: list[HalfPlane], n: int = 5) -> list[Point]:
      """Sample points on the line within the intersection of half-plane constraints and near existing points."""
      # Parameterize the line: L(t) = P0 + t * d
      # P0 is a point on the line, d is the direction vector

      # Get the direction vector (dx, dy) of the line
      a, b, c = self.coefficients
      if abs(a) > ATOM and abs(b) > ATOM:
          # General case: direction vector perpendicular to normal vector (a, b)
          d = Point(-b, a)
      elif abs(a) > ATOM:
          # Vertical line
          d = Point(0, 1)
      elif abs(b) > ATOM:
          # Horizontal line
          d = Point(1, 0)
      else:
          raise ValueError("Invalid line with zero coefficients")

      # Find a point P0 on the line
      if abs(a) > ATOM:
          x0 = (-c - b * 0) / a  # Set y = 0
          y0 = 0
      elif abs(b) > ATOM:
          x0 = 0
          y0 = (-c - a * 0) / b  # Set x = 0
      else:
          raise ValueError("Invalid line with zero coefficients")

      P0 = Point(x0, y0)

      # Project existing points onto the line to get an initial interval
      t_points = []
      for p in points:
          # Vector from P0 to p
          vec = p - P0
          # Project vec onto d
          t = (vec.x * d.x + vec.y * d.y) / (d.x ** 2 + d.y ** 2)
          t_points.append(t)
      if not t_points:
          raise ValueError("No existing points provided for sampling")

      # Determine the interval based on existing points
      t_points.sort()
      t_center = sum(t_points) / len(t_points)
      t_radius = max(abs(t - t_center) for t in t_points)

      # Define an initial interval around the existing points
      t_init_min = t_center - t_radius
      t_init_max = t_center + t_radius

      # Initialize the interval as [t_init_min, t_init_max]
      t_min = t_init_min
      t_max = t_init_max

      # Process half-plane constraints
      for hp in halfplanes:
          # For each half-plane, compute K and H0
          a_h, b_h, c_h = hp.line.coefficients
          sign_h = hp.sign  # +1 or -1

          # Compute K = a_h * dx + b_h * dy
          K = a_h * d.x + b_h * d.y

          # Compute H0 = a_h * x0 + b_h * y0 + c_h
          H0 = a_h * P0.x + b_h * P0.y + c_h

          # The half-plane inequality is sign_h * (K * t + H0) >= 0
          S = sign_h

          if abs(K) < ATOM:
              # K is zero
              if S * H0 >= 0:
                  # The entire line satisfies the constraint
                  continue
              else:
                  # The line is entirely outside the half-plane
                  return []
          else:
              t0 = -H0 / K
              if K * S > 0:
                  # Inequality is t >= t0
                  t_min = max(t_min, t0)
              else:
                  # Inequality is t <= t0
                  t_max = min(t_max, t0)

      # After processing all half-planes, check if the interval is valid
      if t_min > t_max:
          # Empty interval
          return []
      else:
          # The intersection is [t_min, t_max]
          # Sample n points within this interval
          result = None
          best = -1.0
          for _ in range(n):
              t = unif(t_min, t_max)
              p = Point(P0.x + t * d.x, P0.y + t * d.y)
              # Calculate the minimum distance to existing points
              mind = min(p.distance(q) for q in points)
              if mind > best:
                  best = mind
                  result = p
          if result is None:
              raise ValueError("Cannot find a suitable point within the constraints")
          return [result]