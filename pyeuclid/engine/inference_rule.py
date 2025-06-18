from __future__ import annotations
from typing import Iterable
from pyeuclid.formalization.relation import *
from pyeuclid.formalization.utils import *
from sympy import Rational, pi, sin, cos


inference_rule_sets = {}


class register():
    def __init__(self, *annotations):
        self.annotations = annotations

    def __call__(self, cls):
        for item in self.annotations:
            if not item in inference_rule_sets:
                inference_rule_sets[item] = [cls]
            else:
                inference_rule_sets[item].append(cls)
        
        def format_condition(self):
            result = self._condition()
            if isinstance(result, Iterable):
                return list(result)
            return [result]
        
        def format_conclusion(self):
            result = self._conclusion()
            if isinstance(result, Iterable):
                return list(result)
            return [result]
        
        cls._condition = cls.condition        
        cls._conclusion = cls.conclusion
        cls.condition = format_condition
        cls.conclusion = format_conclusion
            
        return cls


def equal(*lst):
    result = []
    for i in range(len(lst)):
        for j in range(i+1, len(lst)):
            result.append(lst[i]-lst[j])
    return result

class InferenceRule:
    def __init__(self):
        pass

    def condition(self):
        pass

    def conclusion(self):
        pass

    def degenerate(self):
        return False

    def __str__(self):
        class_name = self.__class__.__name__
        content = []
        for key, value in vars(self).items():
            if key.startswith("_") or key == "depth":
                continue
            if not isinstance(value, Iterable):
                content.append(str(value))
            else:
                content.append(','.join(str(i) for i in value))
        attributes = ','.join(content)
        return f"{class_name}({attributes})"

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return str(self) == str(other)

    def __hash__(self):
        return hash(str(self))


def trivial_inference(item):
    for source in getattr(item, "sources", []):
        if type(source) in (DiagramAngle4a, DiagramAngle4b, DiagramAngle2, FlatAngle):
            return True
    return False

@register("basic")
class DefinitionOfMidpoint(InferenceRule):
    """ Definition of Midpoint """
    def __init__(self, a: Point, b: Point, c: Point):
        super().__init__()
        self.a, self.b, self.c = a, b, c
    
    def condition(self):
        return Length(self.a, self.b) - Length(self.a, self.c), Between(self.a, self.b, self.c), Lt(self.b, self.c)
    
    def conclusion(self):
        return Midpoint(self.a, self.b, self.c)

@register("basic")
class DefinitionOfMidpoint1(InferenceRule):
    """ Definition of Midpoint """
    def __init__(self, a: Point, b: Point, c: Point):
        super().__init__()
        self.a, self.b, self.c = a, b, c
    
    def condition(self):
        return Length(self.a, self.b)/Length(self.b, self.c) - Rational(1,2), Between(self.a, self.b, self.c)
    
    def conclusion(self):
        return Midpoint(self.a, self.b, self.c)


@register("basic")
class PropertyOfMidpoint(InferenceRule):
    """ Property of Midpoint """
    def __init__(self, a: Point, b: Point, c: Point):
        super().__init__()
        self.a, self.b, self.c = a, b, c
    
    def condition(self):
        return Midpoint(self.a, self.b, self.c), Lt(self.b, self.c)
    
    def conclusion(self):
        return [
            Length(self.a, self.b) - Length(self.a, self.c),
            Length(self.a, self.b) - Length(self.b, self.c) / 2,
            Length(self.a, self.c) - Length(self.b, self.c) / 2,
            Between(self.a, self.b, self.c)
        ]


@register("basic")
class PropertyOfCongruent(InferenceRule):
    """ Property of Triangle Congruence """
    def __init__(self, a: Point, b: Point, c: Point, p: Point, q: Point, r: Point):
        super().__init__()
        self.a, self.b, self.c, self.p, self.q, self.r = a, b, c, p, q, r
    
    def condition(self):
        return Congruent(self.a, self.b, self.c, self.p, self.q, self.r), Lt(self.a, self.b), Lt(self.b, self.c), Leq(self.a, self.p)
    
    def degenerate(self):
        return self.a == self.p and self.b == self.q and self.c == self.r
    
    def conclusion(self):
        return [
            Length(self.a, self.b) - Length(self.p, self.q),
            Length(self.b, self.c) - Length(self.q, self.r),
            Length(self.c, self.a) - Length(self.r, self.p),
            Angle(self.a, self.b, self.c) - Angle(self.p, self.q, self.r),
            Angle(self.b, self.c, self.a) - Angle(self.q, self.r, self.p),
            Angle(self.c, self.a, self.b) - Angle(self.r, self.p, self.q),
        ]


@register("basic")
class PropertyOfSimilar(InferenceRule):
    """ Property of Similar Triangles """
    def __init__(self, a: Point, b: Point, c: Point, p: Point, q: Point, r: Point):
        super().__init__()
        self.a, self.b, self.c, self.p, self.q, self.r = a, b, c, p, q, r
    
    def condition(self):
        return Similar(self.a, self.b, self.c, self.p, self.q, self.r), Lt(self.a, self.b), Lt(self.b, self.c), Leq(self.a, self.p)
    
    def degenerate(self):
        return self.a == self.p and self.b == self.q and self.c == self.r
    
    def conclusion(self):
        return [
            *equal(Length(self.a, self.b) / Length(self.p, self.q), Length(self.b, self.c) / Length(self.q, self.r), Length(self.c, self.a) / Length(self.r, self.p)),
            Length(self.a, self.b)/Length(self.b, self.c) - Length(self.p, self.q)/Length(self.q, self.r),
            Length(self.a, self.b)/Length(self.c, self.a) - Length(self.p, self.q)/Length(self.r, self.p),
            Length(self.b, self.c)/Length(self.c, self.a) - Length(self.q, self.r)/Length(self.r, self.p),
            Angle(self.a, self.b, self.c) - Angle(self.p, self.q, self.r),
            Angle(self.b, self.c, self.a) - Angle(self.q, self.r, self.p),
            Angle(self.c, self.a, self.b) - Angle(self.r, self.p, self.q),
        ]

@register("ex")
class DefinitionOfTriangle(InferenceRule):
    def __init__(self, a: Point, b: Point, c: Point):
        super().__init__()
        self.a, self.b, self.c = a, b, c
    
    def condition(self):
        return Not(Collinear(self.a, self.b, self.c)), Lt(self.a, self.b), Lt(self.b, self.c)
    
    def conclusion(self):
        return Triangle(self.a, self.b, self.c)


@register("ex")
class PropertyOfTriangle(InferenceRule):
    def __init__(self, a: Point, b: Point, c: Point):
        super().__init__()
        self.a, self.b, self.c = a, b, c
    
    def condition(self):
        return Triangle(self.a, self.b, self.c), Lt(self.a, self.b), Lt(self.b, self.c)
    
    def conclusion(self):
        return [
            Not(Collinear(self.a, self.b, self.c)), 
            Angle(self.b, self.a, self.c) + Angle(self.c, self.b, self.a) + Angle(self.a, self.c, self.b) - pi
        ]


@register("ex")
class DefinitionOfQuadrilateral(InferenceRule):
    def __init__(self, p1: Point, p2: Point, p3: Point, p4: Point):
        super().__init__()
        self.p1, self.p2, self.p3, self.p4 = p1, p2, p3, p4
    
    def condition(self):
        return [
            OppositeSide(self.p1, self.p3, self.p2, self.p4),
            OppositeSide(self.p2, self.p4, self.p1, self.p3),
            Not(Collinear(self.p1, self.p2, self.p3)),
            Not(Collinear(self.p2, self.p3, self.p4)),
            Not(Collinear(self.p3, self.p4, self.p1)),
            Not(Collinear(self.p4, self.p1, self.p2)),
            Lt(self.p1, self.p2),
            Lt(self.p1, self.p3),
            Lt(self.p1, self.p4),
            Lt(self.p2, self.p4),
        ]
    
    def conclusion(self):
        return Quadrilateral(self.p1, self.p2, self.p3, self.p4)


@register("ex")
class PropertyOfQuadrilateral(InferenceRule):
    def __init__(self, p1: Point, p2: Point, p3: Point, p4: Point):
        super().__init__()
        self.p1, self.p2, self.p3, self.p4 = p1, p2, p3, p4
    
    def condition(self):
        return Quadrilateral(self.p1, self.p2, self.p3, self.p4), Lt(self.p1, self.p2), Lt(self.p1, self.p3), Lt(self.p1, self.p4), Lt(self.p2, self.p4)
    
    def conclusion(self):
        return [
            # Angle(self.p4, self.p1, self.p2) + Angle(self.p1, self.p2, self.p3) + Angle(self.p2, self.p3, self.p4) + Angle(self.p3, self.p4, self.p1) - 2 * pi,
            OppositeSide(self.p1, self.p3, self.p2, self.p4),
            OppositeSide(self.p2, self.p4, self.p1, self.p3),
            Not(Collinear(self.p1, self.p2, self.p3)),
            Not(Collinear(self.p2, self.p3, self.p4)),
            Not(Collinear(self.p3, self.p4, self.p1)),
            Not(Collinear(self.p4, self.p1, self.p2)),
        ]


@register("basic")
class DefinitionOfParallelogram1(InferenceRule):
    """ Definition of Parallelogram """
    def __init__(self, p1: Point, p2: Point, p3: Point, p4: Point):
        super().__init__()
        self.p1, self.p2, self.p3, self.p4 = p1, p2, p3, p4
    
    def condition(self):
        return [
            Quadrilateral(self.p1, self.p2, self.p3, self.p4),
            Parallel(self.p1, self.p2, self.p3, self.p4),
            Parallel(self.p1, self.p4, self.p2, self.p3),
            Lt(self.p1, self.p2),
            Lt(self.p1, self.p3),
            Lt(self.p1, self.p4),
            Lt(self.p2, self.p4),
        ]
    
    def conclusion(self):
        return Parallelogram(self.p1, self.p2, self.p3, self.p4)


@register("basic")
class DefinitionOfParallelogram2(InferenceRule):
    """ Definition of Parallelogram """
    def __init__(self, p1: Point, p2: Point, p3: Point, p4: Point):
        super().__init__()
        self.p1, self.p2, self.p3, self.p4 = p1, p2, p3, p4
    
    def condition(self):
        return [
            Quadrilateral(self.p1, self.p2, self.p3, self.p4),
            Parallel(self.p1, self.p2, self.p3, self.p4),
            Length(self.p1, self.p2) - Length(self.p3, self.p4),
            Lt(self.p1, self.p2),
            Lt(self.p1, self.p3),
            Lt(self.p1, self.p4),
        ]
    
    def conclusion(self):
        return Parallelogram(self.p1, self.p2, self.p3, self.p4)


@register("basic")
class DefinitionOfParallelogram3(InferenceRule):
    """ Definition of Parallelogram """
    def __init__(self, p1: Point, p2: Point, p3: Point, p4: Point):
        super().__init__()
        self.p1, self.p2, self.p3, self.p4 = p1, p2, p3, p4
    
    def condition(self):
        return [
            Quadrilateral(self.p1, self.p2, self.p3, self.p4),
            Length(self.p1, self.p2) - Length(self.p3, self.p4),
            Length(self.p1, self.p4) - Length(self.p2, self.p3),
            Lt(self.p1, self.p2),
            Lt(self.p1, self.p3),
            Lt(self.p1, self.p4),
            Lt(self.p2, self.p4),
        ]
    
    def conclusion(self):
        return Parallelogram(self.p1, self.p2, self.p3, self.p4)


@register("basic")
class DefinitionOfParallelogram4(InferenceRule):
    """ Definition of Parallelogram """
    def __init__(self, p1: Point, p2: Point, p3: Point, p4: Point):
        super().__init__()
        self.p1, self.p2, self.p3, self.p4 = p1, p2, p3, p4
    
    def condition(self):
        return [
            Quadrilateral(self.p1, self.p2, self.p3, self.p4),
            Angle(self.p4, self.p1, self.p2) - Angle(self.p2, self.p3, self.p4),
            Angle(self.p1, self.p2, self.p3) - Angle(self.p3, self.p4, self.p1),
            Lt(self.p1, self.p2),
            Lt(self.p1, self.p3),
            Lt(self.p1, self.p4),
            Lt(self.p2, self.p4),
        ]
    
    def conclusion(self):
        return Parallelogram(self.p1, self.p2, self.p3, self.p4)


@register("basic")
class PropertyOfParallelogram(InferenceRule):
    """ Property of Parallelogram """
    def __init__(self, p1: Point, p2: Point, p3: Point, p4: Point):
        super().__init__()
        self.p1, self.p2, self.p3, self.p4 = p1, p2, p3, p4
    
    def condition(self):
        return Parallelogram(self.p1, self.p2, self.p3, self.p4)
    
    def conclusion(self):
        return [
            Quadrilateral(self.p1, self.p2, self.p3, self.p4),
            Parallel(self.p1, self.p2, self.p3, self.p4),
            Parallel(self.p1, self.p4, self.p2, self.p3),
            Length(self.p1, self.p2) - Length(self.p3, self.p4),
            Length(self.p1, self.p4) - Length(self.p2, self.p3),
            Angle(self.p4, self.p1, self.p2) + Angle(self.p1, self.p2, self.p3) - pi,
            Angle(self.p1, self.p2, self.p3) + Angle(self.p2, self.p3, self.p4) - pi,
            Angle(self.p2, self.p3, self.p4) + Angle(self.p3, self.p4, self.p1) - pi,
            Angle(self.p3, self.p4, self.p1) + Angle(self.p4, self.p1, self.p2) - pi,
            Angle(self.p4, self.p1, self.p2) - Angle(self.p2, self.p3, self.p4),
            Angle(self.p1, self.p2, self.p3) - Angle(self.p3, self.p4, self.p1),
        ]


@register("basic")
class DefinitionOfRectangle1(InferenceRule):
    """ Definition of Rectangle """
    def __init__(self, p1: Point, p2: Point, p3: Point, p4: Point):
        super().__init__()
        self.p1, self.p2, self.p3, self.p4 = p1, p2, p3, p4
    
    def condition(self):
        return [
            Parallelogram(self.p1, self.p2, self.p3, self.p4),
            Angle(self.p1, self.p2, self.p3) - pi / 2
        ]
    
    def conclusion(self):
        return Rectangle(self.p1, self.p2, self.p3, self.p4)


@register("basic")
class DefinitionOfRectangle2(InferenceRule):
    """ Definition of Rectangle """
    def __init__(self, p1: Point, p2: Point, p3: Point, p4: Point):
        super().__init__()
        self.p1, self.p2, self.p3, self.p4 = p1, p2, p3, p4
    
    def condition(self):
        return [
            Parallelogram(self.p1, self.p2, self.p3, self.p4),
            Length(self.p1, self.p3) - Length(self.p2, self.p4),
            Lt(self.p1, self.p2),
            Lt(self.p1, self.p3),
            Lt(self.p1, self.p4),
            Lt(self.p2, self.p4),
        ]
    
    def conclusion(self):
        return Rectangle(self.p1, self.p2, self.p3, self.p4)


@register("basic")
class PropertyOfRectangle(InferenceRule):
    """ Property of Rectangle """
    def __init__(self, p1: Point, p2: Point, p3: Point, p4: Point):
        super().__init__()
        self.p1, self.p2, self.p3, self.p4 = p1, p2, p3, p4
    
    def condition(self):
        return Rectangle(self.p1, self.p2, self.p3, self.p4)
    
    def conclusion(self):
        return [
            Parallelogram(self.p1, self.p2, self.p3, self.p4),
            Length(self.p1, self.p3) - Length(self.p2, self.p4),
            Angle(self.p4, self.p1, self.p2) - pi / 2,
            Angle(self.p1, self.p2, self.p3) - pi / 2,
            Angle(self.p2, self.p3, self.p4) - pi / 2,
            Angle(self.p3, self.p4, self.p1) - pi / 2,
        ]


@register("basic")
class DefinitionOfRhombus1(InferenceRule):
    """ Definition of Rhombus """
    def __init__(self, p1: Point, p2: Point, p3: Point, p4: Point):
        super().__init__()
        self.p1, self.p2, self.p3, self.p4 = p1, p2, p3, p4
    
    def condition(self):
        return [
            Length(self.p1, self.p2) - Length(self.p2, self.p3),
            Length(self.p2, self.p3) - Length(self.p3, self.p4),
            Length(self.p3, self.p4) - Length(self.p4, self.p1),
            Lt(self.p1, self.p2),
            Lt(self.p1, self.p3),
            Lt(self.p1, self.p4),
            Lt(self.p2, self.p4),
        ]
    
    def conclusion(self):
        return Rhombus(self.p1, self.p2, self.p3, self.p4)


@register("basic")
class DefinitionOfRhombus2(InferenceRule):
    """ Definition of Rhombus """
    def __init__(self, p1: Point, p2: Point, p3: Point, p4: Point):
        super().__init__()
        self.p1, self.p2, self.p3, self.p4 = p1, p2, p3, p4
    
    def condition(self):
        return [
            Parallelogram(self.p1, self.p2, self.p3, self.p4),
            Length(self.p1, self.p2) - Length(self.p2, self.p3),
            Lt(self.p1, self.p3)
        ]
    
    def conclusion(self):
        return Rhombus(self.p1, self.p2, self.p3, self.p4)


@register("basic")
class DefinitionOfRhombus3(InferenceRule):
    """ Definition of Rhombus """
    def __init__(self, p1: Point, p2: Point, p3: Point, p4: Point):
        super().__init__()
        self.p1, self.p2, self.p3, self.p4 = p1, p2, p3, p4
    
    def condition(self):
        return [
            Parallelogram(self.p1, self.p2, self.p3, self.p4),
            Perpendicular(self.p1, self.p3, self.p2, self.p4),
            Lt(self.p1, self.p2),
            Lt(self.p1, self.p3),
            Lt(self.p1, self.p4),
            Lt(self.p2, self.p4),
        ]
    
    def conclusion(self):
        return Rhombus(self.p1, self.p2, self.p3, self.p4)


@register("basic")
class DefinitionOfRhombus4(InferenceRule):
    """ Definition of Rhombus """
    def __init__(self, p1: Point, p2: Point, p3: Point, p4: Point):
        super().__init__()
        self.p1, self.p2, self.p3, self.p4 = p1, p2, p3, p4
    
    def condition(self):
        return [
            Parallelogram(self.p1, self.p2, self.p3, self.p4),
            Angle(self.p1, self.p2, self.p4) - Angle(self.p3, self.p2, self.p4),
            Lt(self.p1, self.p3),
        ]
    
    def conclusion(self):
        return Rhombus(self.p1, self.p2, self.p3, self.p4)


@register("basic")
class PropertyOfRhombus(InferenceRule):
    """ Property of Rhombus """
    def __init__(self, p1: Point, p2: Point, p3: Point, p4: Point):
        super().__init__()
        self.p1, self.p2, self.p3, self.p4 = p1, p2, p3, p4
    
    def condition(self):
        return Rhombus(self.p1, self.p2, self.p3, self.p4)
    
    def conclusion(self):
        return [
            Parallelogram(self.p1, self.p2, self.p3, self.p4),
            *equal(Length(self.p1, self.p2), Length(self.p2, self.p3), Length(self.p3, self.p4), Length(self.p4, self.p1)),
            Perpendicular(self.p1, self.p3, self.p2, self.p4),
            *equal(Angle(self.p2, self.p1, self.p3), Angle(self.p3, self.p1, self.p4), Angle(self.p2, self.p3, self.p1), Angle(self.p1, self.p3, self.p4)),
            *equal(Angle(self.p1, self.p2, self.p4), Angle(self.p1, self.p4, self.p2), Angle(self.p3, self.p2, self.p4), Angle(self.p3, self.p4, self.p2))
        ]


@register("basic")
class DefinitionOfSquare1(InferenceRule):
    """ Definition of Square """
    def __init__(self, p1: Point, p2: Point, p3: Point, p4: Point):
        super().__init__()
        self.p1, self.p2, self.p3, self.p4 = p1, p2, p3, p4
    
    def condition(self):
        return [
            Rectangle(self.p1, self.p2, self.p3, self.p4),
            Length(self.p1, self.p2) - Length(self.p1, self.p4),
            Lt(self.p2, self.p4),
        ]
    
    def conclusion(self):
        return Square(self.p1, self.p2, self.p3, self.p4)


@register("basic")
class DefinitionOfSquare2(InferenceRule):
    """ Definition of Square """
    def __init__(self, p1: Point, p2: Point, p3: Point, p4: Point):
        super().__init__()
        self.p1, self.p2, self.p3, self.p4 = p1, p2, p3, p4
    
    def condition(self):
        return [
            Rhombus(self.p1, self.p2, self.p3, self.p4),
            Angle(self.p1, self.p2, self.p3) - pi / 2,
            Lt(self.p1, self.p3),
        ]
    
    def conclusion(self):
        return Square(self.p1, self.p2, self.p3, self.p4)


@register("basic")
class DefinitionOfSquare3(InferenceRule):
    """ Definition of Square """
    def __init__(self, p1: Point, p2: Point, p3: Point, p4: Point):
        super().__init__()
        self.p1, self.p2, self.p3, self.p4 = p1, p2, p3, p4
    
    def condition(self):
        return [
            Rhombus(self.p1, self.p2, self.p3, self.p4),
            Length(self.p1, self.p3) - Length(self.p2, self.p4),
            Lt(self.p1, self.p2),
            Lt(self.p1, self.p3),
            Lt(self.p1, self.p4),
            Lt(self.p2, self.p4),
        ]
    
    def conclusion(self):
        return Square(self.p1, self.p2, self.p3, self.p4)


@register("basic")
class PropertyOfSquare(InferenceRule):
    """ Property of Square """
    def __init__(self, p1: Point, p2: Point, p3: Point, p4: Point):
        super().__init__()
        self.p1, self.p2, self.p3, self.p4 = p1, p2, p3, p4
    
    def condition(self):
        return Square(self.p1, self.p2, self.p3, self.p4)
    
    def conclusion(self):
        return [
            Rectangle(self.p1, self.p2, self.p3, self.p4),
            Rhombus(self.p1, self.p2, self.p3, self.p4),
        ]


@register("basic")
class DefinitionOfTrapezoid(InferenceRule):
    """ Definition of Trapezoid """
    def __init__(self, p1: Point, p2: Point, p3: Point, p4: Point):
        super().__init__()
        self.p1, self.p2, self.p3, self.p4 = p1, p2, p3, p4
    
    def condition(self):
        return [
            Quadrilateral(self.p1, self.p2, self.p3, self.p4),
            Parallel(self.p1, self.p2, self.p3, self.p4),
            Lt(self.p1, self.p2),
            Lt(self.p1, self.p3),
            Lt(self.p1, self.p4),
        ]
    
    def conclusion(self):
        return Trapezoid(self.p1, self.p2, self.p3, self.p4)


@register("basic")
class PropertyOfTrapezoid(InferenceRule):
    """ Definition of Trapezoid """
    def __init__(self, p1: Point, p2: Point, p3: Point, p4: Point):
        super().__init__()
        self.p1, self.p2, self.p3, self.p4 = p1, p2, p3, p4
    
    def condition(self):
        return [
            Trapezoid(self.p1, self.p2, self.p3, self.p4),
            Parallel(self.p1, self.p2, self.p3, self.p4),
        ]
    
    def conclusion(self):
        return [
            Quadrilateral(self.p1, self.p2, self.p3, self.p4),
            Angle(self.p1, self.p2, self.p3) + Angle(self.p2, self.p3, self.p4) - pi,
            Angle(self.p4, self.p1, self.p2) + Angle(self.p3, self.p4, self.p1) - pi,
        ]


@register("basic")
class DefinitionOfKite1(InferenceRule):
    """ Definition of Kite """
    def __init__(self, p1: Point, p2: Point, p3: Point, p4: Point):
        super().__init__()
        self.p1, self.p2, self.p3, self.p4 = p1, p2, p3, p4
    
    def condition(self):
        return [
            Quadrilateral(self.p1, self.p2, self.p3, self.p4),
            Length(self.p1, self.p2) - Length(self.p2, self.p3),
            Length(self.p3, self.p4) - Length(self.p4, self.p1),
        ]
    
    def conclusion(self):
        return Kite(self.p1, self.p2, self.p3, self.p4)


@register("basic")
class PropertyOfKite(InferenceRule):
    """ Property of Kite """
    def __init__(self, p1: Point, p2: Point, p3: Point, p4: Point):
        super().__init__()
        self.p1, self.p2, self.p3, self.p4 = p1, p2, p3, p4
    
    def condition(self):
        return [
            Kite(self.p1, self.p2, self.p3, self.p4),
            Length(self.p1, self.p2) - Length(self.p2, self.p3),
            Length(self.p3, self.p4) - Length(self.p4, self.p1),
        ]
    
    def conclusion(self):
        return [
            Quadrilateral(self.p1, self.p2, self.p3, self.p4),
            Perpendicular(self.p1, self.p3, self.p2, self.p4),
            Angle(self.p2, self.p1, self.p4) - Angle(self.p2, self.p3, self.p4),
            Angle(self.p1, self.p2, self.p4) - Angle(self.p3, self.p2, self.p4),
            Angle(self.p1, self.p4, self.p2) - Angle(self.p3, self.p4, self.p2),
        ]


@register("basic")
class DefinitionOfIncenter1(InferenceRule):
    """ Definition of Incenter """
    def __init__(self, o: Point, a: Point, b: Point, c: Point):
        super().__init__()
        self.o, self.a, self.b, self.c = o, a, b, c
    
    def condition(self):
        return [
            Triangle(self.a, self.b, self.c),
            Angle(self.a, self.b, self.o) - Angle(self.c, self.b, self.o),
            Angle(self.a, self.c, self.o) - Angle(self.b, self.c, self.o),
            Lt(self.b, self.c)
        ]
    
    def conclusion(self):
        return Incenter(self.o, self.a, self.b, self.c)


@register("basic")
class DefinitionOfIncenter2(InferenceRule):
    """ Definition of Incenter """
    def __init__(self, o: Point, a: Point, b: Point, c: Point, p: Point, q: Point, r: Point):
        super().__init__()
        self.o, self.a, self.b, self.c, self.p, self.q, self.r = o, a, b, c, p, q, r
    
    def condition(self):
        return [
            Triangle(self.a, self.b, self.c),
            Collinear(self.p, self.a, self.b),
            Collinear(self.q, self.b, self.c),
            Collinear(self.r, self.c, self.a),
            SameSide(self.o, self.a, self.b, self.c),
            SameSide(self.o, self.b, self.c, self.a),
            SameSide(self.o, self.c, self.a, self.b),
            Perpendicular(self.o, self.p, self.a, self.b),
            Perpendicular(self.o, self.q, self.b, self.c),
            Perpendicular(self.o, self.r, self.c, self.a),
            Length(self.o, self.p) - Length(self.o, self.q),
            Length(self.o, self.q) - Length(self.o, self.r),
            Lt(self.a, self.b),
            Lt(self.b, self.c)
        ]
    
    def conclusion(self):
        return Incenter(self.o, self.a, self.b, self.c)


@register("basic")
class PropertyOfIncenter1(InferenceRule):
    """ Property of Incenter """
    def __init__(self, o: Point, a: Point, b: Point, c: Point):
        super().__init__()
        self.o, self.a, self.b, self.c = o, a, b, c
    
    def condition(self):
        return Incenter(self.o, self.a, self.b, self.c)
    
    def conclusion(self):
        return [
            Angle(self.b, self.a, self.o) - Angle(self.c, self.a, self.o),
            Angle(self.a, self.b, self.o) - Angle(self.c, self.b, self.o),
            Angle(self.a, self.c, self.o) - Angle(self.b, self.c, self.o),
        ]


@register("basic")
class PropertyOfIncenter2(InferenceRule):
    """ Property of Incenter """
    def __init__(self, o: Point, a: Point, b: Point, c: Point, p: Point, q: Point):
        super().__init__()
        self.o, self.a, self.b, self.c, self.p, self.q = o, a, b, c, p, q
    
    def condition(self):
        return [
            Incenter(self.o, self.a, self.b, self.c),
            Collinear(self.a, self.b, self.p),
            Collinear(self.b, self.c, self.q),
            Perpendicular(self.o, self.p, self.a, self.b),
            Perpendicular(self.o, self.q, self.b, self.c),
        ]
    
    def conclusion(self):
        return [
            Length(self.o, self.p) - Length(self.o, self.q)
        ]


@register("basic")
class DefinitionOfCentroid1(InferenceRule):
    """ Definition of Centroid """
    def __init__(self, o: Point, a: Point, b: Point, c: Point, p: Point, q: Point):
        super().__init__()
        self.o, self.a, self.b, self.c, self.p, self.q = o, a, b, c, p, q
    
    def condition(self):
        return [
            Triangle(self.a, self.b, self.c),
            Midpoint(self.p, self.a, self.b),
            Midpoint(self.q, self.b, self.c),
            Collinear(self.c, self.o, self.p),
            Collinear(self.a, self.o, self.q),
        ]
    
    def conclusion(self):
        return Centroid(self.o, self.a, self.b, self.c)


@register("basic")
class DefinitionOfCentroid2(InferenceRule):
    """ Definition of Centroid """
    def __init__(self, o: Point, a: Point, b: Point, c: Point, p: Point):
        super().__init__()
        self.o, self.a, self.b, self.c, self.p = o, a, b, c, p
    
    def condition(self):
        return [
            Triangle(self.a, self.b, self.c),
            Midpoint(self.p, self.a, self.b),
            Collinear(self.c, self.o, self.p),
            Length(self.o, self.p)/Length(self.o, self.c) - Rational(1,2)
        ]
    
    def conclusion(self):
        return Centroid(self.o, self.a, self.b, self.c)


@register("basic")
class PropertyOfCentroid(InferenceRule):
    """ Property of Centroid """
    def __init__(self, o: Point, a: Point, b: Point, c: Point, p: Point):
        super().__init__()
        self.o, self.a, self.b, self.c, self.p = o, a, b, c, p
    
    def condition(self):
        return [
            Centroid(self.o, self.a, self.b, self.c),
            Collinear(self.p, self.a, self.b),
            Collinear(self.p, self.o, self.c),
        ]
    
    def conclusion(self):
        return [
            Midpoint(self.p, self.a, self.b),
            Length(self.o, self.p)/Length(self.o, self.c) - 1/2
        ]


@register("basic")
class DefinitionOfOrthocenter(InferenceRule):
    """ Definition of Orthocenter """
    def __init__(self, o: Point, a: Point, b: Point, c: Point):
        super().__init__()
        self.o, self.a, self.b, self.c = o, a, b, c
    
    def condition(self):
        return [
            Triangle(self.a, self.b, self.c),
            Perpendicular(self.o, self.a, self.b, self.c),
            Perpendicular(self.o, self.b, self.a, self.c),
            Different2(self.o, self.a),
            Different2(self.o, self.b),
            Different2(self.o, self.c),
            Lt(self.a, self.b)
        ]
    
    def conclusion(self):
        return Orthocenter(self.o, self.a, self.b, self.c)


@register("basic")
class PropertyOfOrthocenter(InferenceRule):
    """ Property of Orthocenter """
    def __init__(self, o: Point, a: Point, b: Point, c: Point):
        super().__init__()
        self.o, self.a, self.b, self.c = o, a, b, c
    
    def condition(self):
        return [
            Orthocenter(self.o, self.a, self.b, self.c),
            Different2(self.o, self.a),
            Different2(self.o, self.b),
            Different2(self.o, self.c),
            Lt(self.a, self.b),
            Lt(self.b, self.c)
        ]
    
    def conclusion(self):
        return [
            Perpendicular(self.o, self.a, self.b, self.c),
            Perpendicular(self.o, self.b, self.c, self.a),
            Perpendicular(self.o, self.c, self.a, self.b),
        ]


@register("basic")
class DefinitionOfCircumcenter(InferenceRule):
    """ Definition of Circumcenter """
    def __init__(self, o: Point, a: Point, b: Point, c: Point):
        super().__init__()
        self.o, self.a, self.b, self.c = o, a, b, c
    
    def condition(self):
        return [
            Triangle(self.a, self.b, self.c),
            Length(self.o, self.a) - Length(self.o, self.b),
            Length(self.o, self.b) - Length(self.o, self.c),
            Lt(self.a, self.c)
        ]
    
    def conclusion(self):
        return Circumcenter(self.o, self.a, self.b, self.c)


@register("basic")
class PropertyOfCircumcenter(InferenceRule):
    """ Property of Circumcenter """
    def __init__(self, o: Point, a: Point, b: Point, c: Point):
        super().__init__()
        self.o, self.a, self.b, self.c = o, a, b, c
    
    def condition(self):
        return [
            Circumcenter(self.o, self.a, self.b, self.c),
            Lt(self.a, self.b),
            Lt(self.b, self.c)
        ]
    
    def conclusion(self):
        return [
            Length(self.o, self.a) - Length(self.o, self.b),
            Length(self.o, self.b) - Length(self.o, self.c),
            Length(self.o, self.c) - Length(self.o, self.a),
        ]


# @register("basic")
# class DefinitionOfExcenter1(InferenceRule):
#     def __init__(self, o: Point, a: Point, b: Point, c: Point):
#         super().__init__()
#         self.o, self.a, self.b, self.c = o, a, b, c
    
#     def condition(self):
#         return [
#             Triangle(self.a, self.b, self.c),
#             OppositeSide(self.o, self.a, self.b, self.c),
#             SameSide(self.o, self.b, self.c, self.a),
#             SameSide(self.o, self.c, self.a, self.b),
#             Angle(self.o, self.a, self.b) - Angle(self.o, self.a, self.c),
#             2 * Angle(self.o, self.b, self.c) + Angle(self.a, self.b, self.c) - pi,
#         ]
    
#     def conclusion(self):
#         return Excenter(self.o, self.a, self.b, self.c)


# @register("basic")
# class DefinitionOfExcenter2(InferenceRule):
#     def __init__(self, o: Point, a: Point, b: Point, c: Point):
#         super().__init__()
#         self.o, self.a, self.b, self.c = o, a, b, c
    
#     def condition(self):
#         return [
#             Triangle(self.a, self.b, self.c),
#             OppositeSide(self.o, self.a, self.b, self.c),
#             SameSide(self.o, self.b, self.c, self.a),
#             SameSide(self.o, self.c, self.a, self.b),
#             Angle(self.o, self.b, self.c) * 2 + Angle(self.a, self.b, self.c) - pi,
#             Angle(self.o, self.c, self.b) * 2 + Angle(self.a, self.c, self.b) - pi,
#             Lt(self.b, self.c)
#         ]
    
#     def conclusion(self):
#         return Excenter(self.o, self.a, self.b, self.c)


@register("basic")
class DefinitionOfExcenter3(InferenceRule):
    """ Definition of Excenter """
    def __init__(self, o: Point, a: Point, b: Point, c: Point, p: Point, q: Point, r: Point):
        super().__init__()
        self.o, self.a, self.b, self.c, self.p, self.q, self.r = o, a, b, c, p, q, r
    
    def condition(self):
        return [
            Triangle(self.a, self.b, self.c),
            Collinear(self.p, self.a, self.b),
            Collinear(self.q, self.b, self.c),
            Collinear(self.r, self.c, self.a),
            OppositeSide(self.o, self.a, self.b, self.c),
            SameSide(self.o, self.b, self.c, self.a),
            SameSide(self.o, self.c, self.a, self.b),
            Perpendicular(self.o, self.p, self.a, self.b),
            Perpendicular(self.o, self.q, self.b, self.c),
            Perpendicular(self.o, self.r, self.c, self.a),
            Length(self.o, self.p) - Length(self.o, self.q),
            Length(self.o, self.q) - Length(self.o, self.r),
        ]
    
    def conclusion(self):
        return Excenter(self.o, self.a, self.b, self.c)


@register("basic")
class PropertyOfExcenter1(InferenceRule):
    """ Property of Excenter """
    def __init__(self, o: Point, a: Point, b: Point, c: Point):
        super().__init__()
        self.o, self.a, self.b, self.c = o, a, b, c
    
    def condition(self):
        return [
            Excenter(self.o, self.a, self.b, self.c),
            OppositeSide(self.o, self.a, self.b, self.c),
            SameSide(self.o, self.b, self.c, self.a),
            SameSide(self.o, self.c, self.a, self.b),
            Lt(self.b, self.c)
        ]
    
    def conclusion(self):
        return [
            Angle(self.o, self.a, self.b) - Angle(self.o, self.a, self.c),
            Angle(self.o, self.b, self.c) * 2 + Angle(self.a, self.b, self.c) - pi,
            Angle(self.o, self.c, self.b) * 2 + Angle(self.a, self.c, self.b) - pi,
        ]


@register("basic")
class PropertyOfExcenter2(InferenceRule):
    """ Property of Excenter """
    def __init__(self, o: Point, a: Point, b: Point, c: Point, p: Point, q: Point):
        super().__init__()
        self.o, self.a, self.b, self.c, self.p, self.q = o, a, b, c, p, q
    
    def condition(self):
        return [
            Excenter(self.o, self.a, self.b, self.c),
            Collinear(self.p, self.a, self.b),
            Collinear(self.q, self.b, self.c),
            Perpendicular(self.o, self.p, self.a, self.b),
            Perpendicular(self.o, self.q, self.b, self.c),
        ]
    
    def conclusion(self):
        return [
            Length(self.o, self.p) - Length(self.o, self.q),
        ]


@register("basic")
class AlphaGeometry1(InferenceRule):
    """ Perpendiculars give parallel """
    def __init__(self, a: Point, b: Point, c: Point, d: Point, e: Point, f: Point):
        super().__init__()
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        self.e = e
        self.f = f

    def condition(self):
        return Perpendicular(self.a, self.b, self.c, self.d), Perpendicular(self.c, self.d, self.e, self.f), Lt(self.a, self.b), Lt(self.c, self.d), Lt(self.e, self.f), Lt(self.a, self.e)

    def conclusion(self):
        return Parallel(self.a, self.b, self.e, self.f)


@register("basic")
class CollinearTransist(InferenceRule):
    """ Collinearity transitivity """
    def __init__(self, a: Point, b: Point, c: Point, d: Point):
        super().__init__()
        self.a = a
        self.b = b
        self.c = c
        self.d = d

    def condition(self):
        return Collinear(self.a, self.b, self.c), Collinear(self.a, self.b, self.d), Lt(self.a, self.b), Lt(self.c, self.d), *Different(self.a, self.b, self.c, self.d)

    def conclusion(self):
        return Collinear(self.a, self.c, self.d), Collinear(self.b, self.c, self.d)


@register("basic")
class ConcyclicTransist(InferenceRule):
    """ Concyclic Transitivity"""
    def __init__(self, a: Point, b: Point, c: Point, d: Point, e: Point):
        super().__init__()
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        self.e = e

    def condition(self):
        return Concyclic(self.a, self.b, self.c, self.d), Concyclic(self.a, self.b, self.c, self.e), Lt(self.a, self.b), Lt(self.b, self.c), Lt(self.d, self.e), *Different(self.a, self.b, self.c, self.d, self.e)

    def conclusion(self):
        return Concyclic(self.a, self.b, self.d, self.e), Concyclic(self.b, self.c, self.d, self.e), Concyclic(self.a, self.c, self.d, self.e)


@register("basic")
class AlphaGeometry1b(InferenceRule):
    """ Perpendicular + paralel -> perpendicular """
    def __init__(self, a: Point, b: Point, c: Point, d: Point, e: Point, f: Point):
        super().__init__()
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        self.e = e
        self.f = f

    def condition(self):
        return Perpendicular(self.a, self.b, self.c, self.d), Parallel(self.a, self.b, self.e, self.f), Lt(self.a, self.b), Lt(self.c, self.d), Lt(self.e, self.f)

    def conclusion(self):
        return Perpendicular(self.c, self.d, self.e, self.f)


@register("basic")
class AlphaGeometry2(InferenceRule):
    """ Definition of Concyclic """
    def __init__(self, o: Point, a: Point, b: Point, c: Point, d: Point):
        super().__init__()
        self.o = o
        self.a = a
        self.b = b
        self.c = c
        self.d = d

    def condition(self):
        return Length(self.o, self.a) - Length(self.o, self.b), Length(self.o, self.a) - Length(self.o, self.c), Length(self.o, self.a) - Length(self.o, self.d), Lt(self.a, self.b), Lt(self.b, self.c), Lt(self.c, self.d)

    def conclusion(self):
        return Concyclic(self.a, self.b, self.c, self.d)


@register("ex")
class AlphaGeometry3a(InferenceRule):
    """ Parallel From Corresponding Angles """
    def __init__(self, a: Point, b: Point, c: Point, d: Point, e: Point, f: Point):
        super().__init__()
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        self.e = e
        self.f = f

    def condition(self):
        return Angle(self.a, self.b, self.c) - Angle(self.d, self.e, self.f), Parallel(self.b, self.c, self.e, self.f), SameSide(self.a, self.e, self.b, self.c), OppositeSide(self.d, self.b, self.e, self.f), SameSide(self.f, self.c, self.b, self.e)

    def conclusion(self):
        return Parallel(self.b, self.a, self.d, self.e)


@register("basic")
class AlphaGeometry3b(InferenceRule):
    """ Parallel From Corresponding Angles """
    def __init__(self, a: Point, b: Point, c: Point, d: Point, e: Point):
        super().__init__()
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        self.e = e

    def condition(self):
        return Angle(self.b, self.a, self.c) - Angle(self.d, self.e, self.c), Collinear(self.a, self.c, self.e), SameSide(self.b, self.d, self.a, self.c), Not(Between(self.c, self.a, self.e))

    def conclusion(self):
        return Parallel(self.a, self.b, self.d, self.e)


@register("basic")
class AlphaGeometry4a(InferenceRule):
    """ Angles subtended by the same chord (or arc) and on the same side of the chord are equal in a circle """
    def __init__(self, a: Point, b: Point, p: Point, q: Point):
        super().__init__()
        self.a = a
        self.b = b
        self.p = p
        self.q = q

    def condition(self):
        return Concyclic(self.a, self.b, self.p, self.q), Lt(self.a, self.b), Lt(self.p, self.q), SameSide(self.p, self.q, self.a, self.b)

    def conclusion(self):
        return Angle(self.a, self.p, self.b)-Angle(self.a, self.q, self.b),


@register("basic")
class AlphaGeometry4b(InferenceRule):
    """ Angles subtended by the same chord from opposite arcs (sides) sum to π """
    def __init__(self, a: Point, b: Point, p: Point, q: Point):
        super().__init__()
        self.a = a
        self.b = b
        self.p = p
        self.q = q

    def condition(self):
        return Concyclic(self.a, self.b, self.p, self.q), Lt(self.a, self.b), Lt(self.p, self.q), OppositeSide(self.p, self.q, self.a, self.b)

    def conclusion(self):
        return Angle(self.a, self.p, self.b)+Angle(self.a, self.q, self.b)-pi,


@register("basic")
class AlphaGeometry5a(InferenceRule):
    """ If two angles from the same chord to two points on the same side are equal, then the four points lie on a circle """
    def __init__(self, a: Point, b: Point, p: Point, q: Point):
        super().__init__()
        self.a = a
        self.b = b
        self.p = p
        self.q = q

    def condition(self):
        return Not(Collinear(self.p, self.q, self.b)), Not(Collinear(self.p, self.q, self.a)), Not(Collinear(self.b, self.q, self.a)), Not(Collinear(self.p, self.a, self.b)), Angle(self.a, self.p, self.b)-Angle(self.a, self.q, self.b), Lt(self.a, self.b), Lt(self.p, self.q), SameSide(self.p, self.q, self.a, self.b)

    def conclusion(self):
        return Concyclic(self.a, self.b, self.p, self.q)


@register("basic")
class AlphaGeometry5b(InferenceRule):
    """ If two angles from opposite sides of the same chord sum to π, then the points lie on a circle """
    def __init__(self, a: Point, b: Point, p: Point, q: Point):
        super().__init__()
        self.a = a
        self.b = b
        self.p = p
        self.q = q

    def condition(self):
        return Not(Collinear(self.p, self.q, self.b)), Not(Collinear(self.p, self.q, self.a)), Not(Collinear(self.b, self.q, self.a)), Not(Collinear(self.p, self.a, self.b)), Angle(self.a, self.p, self.b)+Angle(self.a, self.q, self.b)-pi, Lt(self.a, self.b), Lt(self.p, self.q), OppositeSide(self.p, self.q, self.a, self.b)

    def conclusion(self):
        return Concyclic(self.a, self.b, self.p, self.q)


@register("basic")
class AlphaGeometry6a(InferenceRule):
    """ If two chords subtend the same angle on the same circle, they are equal in length """
    def __init__(self, a: Point, b: Point, c: Point, p: Point, q: Point, r: Point):
        super().__init__()
        self.a = a
        self.b = b
        self.c = c
        self.p = p
        self.q = q
        self.r = r

    def condition(self):
        return Concyclic(self.a, self.b, self.c, self.p), Concyclic(self.a, self.b, self.c, self.q), Concyclic(self.a, self.b, self.c, self.r), Angle(self.a, self.c, self.b)-Angle(self.p, self.r, self.q), *Different(self.a, self.b), *Different(self.p, self.q)

    def conclusion(self):
        return Length(self.a, self.b)-Length(self.p, self.q)


@register("basic")
class AlphaGeometry6b(InferenceRule):
    """ If two chords subtend angles that are supplementary to each other across a circle, their lengths are equal """
    def __init__(self, a: Point, b: Point, c: Point, p: Point, q: Point, r: Point):
        super().__init__()
        self.a = a
        self.b = b
        self.c = c
        self.p = p
        self.q = q
        self.r = r

    def condition(self):
        return Concyclic(self.a, self.b, self.c, self.p), Concyclic(self.a, self.b, self.c, self.q), Concyclic(self.a, self.b, self.c, self.r), Angle(self.a, self.c, self.b)+Angle(self.p, self.r, self.q)-pi, *Different(self.a, self.b), *Different(self.p, self.q)

    def conclusion(self):
        return Length(self.a, self.b)-Length(self.p, self.q)


@register("basic")
class AlphaGeometry7(InferenceRule):
    """ The segment joining the midpoints of two sides of a triangle is parallel to the third side. """
    def __init__(self, a: Point, b: Point, c: Point, e: Point, f: Point):
        super().__init__()
        self.a = a
        self.b = b
        self.c = c
        self.e = e
        self.f = f

    def condition(self):
        return Midpoint(self.e, self.a, self.b), Midpoint(self.f, self.a, self.c), *Different(self.b, self.c), *Different(self.e, self.f), Lt(self.b, self.c)

    def conclusion(self):
        return Parallel(self.e, self.f, self.b, self.c), Similar(self.a, self.e, self.f, self.a, self.b, self.c)


@register("basic")
class AlphaGeometry8(InferenceRule):
    """ length ratios arising from similar triangles """
    def __init__(self, a: Point, b: Point, c: Point, d: Point, o: Point):
        super().__init__()
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        self.o = o

    def condition(self):
        return Collinear(self.o, self.a, self.c), Collinear(self.o, self.b, self.d), Parallel(self.a, self.b, self.c, self.d), *Different(self.o, self.a, self.b, self.c, self.d), Not(Collinear(self.a, self.c, self.b)), Not(Collinear(self.a, self.c, self.d)), Lt(self.a, self.c), Lt(self.a, self.b), Lt(self.a, self.d)

    def conclusion(self):
        return Length(self.a, self.o)/Length(self.b, self.o)-Length(self.a, self.c)/Length(self.b, self.d), Similar(self.o, self.a, self.b, self.o, self.c, self.d)


@register("basic")
class AlphaGeometry12(InferenceRule):
    """ Inversed Angle Bisector Theorem """
    def __init__(self, a: Point, b: Point, c: Point, d: Point):
        super().__init__()
        self.a = a
        self.b = b
        self.c = c
        self.d = d

    def condition(self):
        return Not(Collinear(self.a, self.b, self.c)), Collinear(self.d, self.b, self.c), Length(self.d, self.b)/Length(self.d, self.c)-Length(self.a, self.b)/Length(self.a, self.c), Lt(self.b, self.c), Between(self.d, self.b, self.c)

    def conclusion(self):
        return Angle(self.b, self.a, self.d)-Angle(self.d, self.a, self.c)


@register("basic")
class AlphaGeometry13(InferenceRule):
    """ Angle Bisector Theorem """
    def __init__(self, a: Point, b: Point, c: Point, d: Point):
        super().__init__()
        self.a = a
        self.b = b
        self.c = c
        self.d = d

    def condition(self):
        return Not(Collinear(self.a, self.b, self.c)), Collinear(self.d, self.b, self.c), Angle(self.b, self.a, self.d) - Angle(self.d, self.a, self.c), *Different(self.a, self.b, self.c, self.d), Lt(self.b, self.c), Between(self.d, self.b, self.c)

    def conclusion(self):
        return Length(self.d, self.b)/Length(self.d, self.c)-Length(self.a, self.b)/Length(self.a, self.c)


@register("basic")
class AlphaGeometry14(InferenceRule):
    """ Isosceles Equal Sides Implies Equal Base Angles """
    def __init__(self, o: Point, a: Point, b: Point):
        super().__init__()
        self.o = o
        self.a = a
        self.b = b

    def condition(self):
        return Not(Collinear(self.o, self.a, self.b)), Length(self.o, self.a)-Length(self.o, self.b), Lt(self.a, self.b)

    def conclusion(self):
        return Angle(self.o, self.a, self.b) - Angle(self.a, self.b, self.o)


@register("basic")
class AlphaGeometry15(InferenceRule):
    """ Isosceles Equal Base Angles Implies Equal Sides """
    def __init__(self, o: Point, a: Point, b: Point):
        super().__init__()
        self.o = o
        self.a = a
        self.b = b

    def condition(self):
        return Not(Collinear(self.o, self.a, self.b)), Angle(self.o, self.a, self.b) - Angle(self.a, self.b, self.o), Lt(self.a, self.b)

    def conclusion(self):
        return Length(self.o, self.a)-Length(self.o, self.b)


@register("basic")
class AlphaGeometry16a(InferenceRule):
    """ the inscribed angle and the tangent angle at the same chord are supplementary """
    def __init__(self, o: Point, a: Point, b: Point, c: Point, x: Point):
        super().__init__()
        self.o = o
        self.a = a
        self.b = b
        self.c = c
        self.x = x

    def condition(self):
        return Length(self.o, self.a) - Length(self.o, self.b), Length(self.o, self.a) - Length(self.o, self.c), Perpendicular(self.o, self.a, self.a, self.x), *Different(self.o, self.a, self.b, self.c, self.x), SameSide(self.x, self.c, self.a, self.b)

    def conclusion(self):
        return Angle(self.x, self.a, self.b)+Angle(self.a, self.c, self.b)-pi


@register("basic")
class AlphaGeometry16b(InferenceRule):
    """ the inscribed angle and the tangent angle at the same chord are equal """
    def __init__(self, o: Point, a: Point, b: Point, c: Point, x: Point):
        super().__init__()
        self.o = o
        self.a = a
        self.b = b
        self.c = c
        self.x = x

    def condition(self):
        return Length(self.o, self.a) - Length(self.o, self.b), Length(self.o, self.a) - Length(self.o, self.c), Perpendicular(self.o, self.a, self.a, self.x), *Different(self.o, self.a, self.b, self.c, self.x), OppositeSide(self.x, self.c, self.a, self.b)

    def conclusion(self):
        return Angle(self.x, self.a, self.b)-Angle(self.a, self.c, self.b)


@register("basic")
class AlphaGeometry17a(InferenceRule):
    """ the inscribed angle and the tangent angle at the same chord are supplementary """
    def __init__(self, o: Point, a: Point, b: Point, c: Point, x: Point):
        super().__init__()
        self.o = o
        self.a = a
        self.b = b
        self.c = c
        self.x = x

    def condition(self):
        return Length(self.o, self.a) - Length(self.o, self.b), Length(self.o, self.a) - Length(self.o, self.c), Angle(self.x, self.a, self.b)+Angle(self.a, self.c, self.b)-pi, *Different(self.o, self.a, self.b, self.c, self.x), Lt(self.a, self.b), SameSide(self.x, self.c, self.a, self.b)

    def conclusion(self):
        return Perpendicular(self.o, self.a, self.a, self.x)


@register("basic")
class AlphaGeometry17b(InferenceRule):
    """ the inscribed angle and the tangent angle at the same chord are equal """
    def __init__(self, o: Point, a: Point, b: Point, c: Point, x: Point):
        super().__init__()
        self.o = o
        self.a = a
        self.b = b
        self.c = c
        self.x = x

    def condition(self):
        return Length(self.o, self.a) - Length(self.o, self.b), Length(self.o, self.a) - Length(self.o, self.c), Angle(self.x, self.a, self.b)-Angle(self.a, self.c, self.b), *Different(self.o, self.a, self.b, self.c, self.x), Lt(self.a, self.b), OppositeSide(self.x, self.c, self.a, self.b)

    def conclusion(self):
        return Perpendicular(self.o, self.a, self.a, self.x)


@register("basic")
class AlphaGeometry18a(InferenceRule):
    """ inscribed angle and half central angles"""
    def __init__(self, o: Point, a: Point, b: Point, c: Point, m: Point):
        super().__init__()
        self.o = o
        self.a = a
        self.b = b
        self.c = c
        self.m = m

    def condition(self):
        return Midpoint(self.m, self.b, self.c), Length(self.o, self.a) - Length(self.o, self.b), Length(self.o, self.a) - Length(self.o, self.c), *Different(self.a, self.b, self.c, self.m, self.o), SameSide(self.a, self.o, self.b, self.c), Lt(self.b, self.c)

    def conclusion(self):
        return Angle(self.b, self.a, self.c)-Angle(self.b, self.o, self.m), Angle(self.b, self.a, self.c)-Angle(self.c, self.o, self.m), Perpendicular(self.o, self.m, self.b, self.c), Congruent3(self.o, self.m, self.b, self.o, self.m, self.c)


@register("basic")
class AlphaGeometry18b(InferenceRule):
    """ inscribed angle and half central angles"""
    def __init__(self, o: Point, a: Point, b: Point, c: Point, m: Point):
        super().__init__()
        self.o = o
        self.a = a
        self.b = b
        self.c = c
        self.m = m

    def condition(self):
        return Midpoint(self.m, self.b, self.c), Length(self.o, self.a) - Length(self.o, self.b), Length(self.o, self.a) - Length(self.o, self.c), *Different(self.a, self.b, self.c, self.m, self.o), OppositeSide(self.a, self.o, self.b, self.c), Lt(self.b, self.c)

    def conclusion(self):
        return Angle(self.b, self.a, self.c) + Angle(self.b, self.o, self.m) - pi, Angle(self.b, self.a, self.c) + Angle(self.c, self.o, self.m) - pi, Perpendicular(self.o, self.m, self.b, self.c), Congruent3(self.o, self.m, self.b, self.o, self.m, self.c)


@register("basic")
class AlphaGeometry19a(InferenceRule):
    """ inscribed angle and half central angles"""
    def __init__(self, o: Point, a: Point, b: Point, c: Point, m: Point):
        super().__init__()
        self.o = o
        self.a = a
        self.b = b
        self.c = c
        self.m = m

    def condition(self):
        return Collinear(self.m, self.b, self.c), Length(self.o, self.a) - Length(self.o, self.b), Length(self.o, self.a) - Length(self.o, self.c), Angle(self.b, self.a, self.c)-Angle(self.b, self.o, self.m), *Different(self.o, self.a, self.b, self.c, self.m), SameSide(self.a, self.o, self.b, self.c), Between(self.m, self.b, self.c)

    def conclusion(self):
        return Midpoint(self.m, self.b, self.c), Angle(self.b, self.a, self.c)-Angle(self.c, self.o, self.m), Perpendicular(self.o, self.m, self.b, self.c), Congruent3(self.o, self.m, self.b, self.o, self.m, self.c)


@register("basic")
class AlphaGeometry19b(InferenceRule):
    """ inscribed angle and half central angles"""
    def __init__(self, o: Point, a: Point, b: Point, c: Point, m: Point):
        super().__init__()
        self.o = o
        self.a = a
        self.b = b
        self.c = c
        self.m = m

    def condition(self):
        return Collinear(self.m, self.b, self.c), Length(self.o, self.a) - Length(self.o, self.b), Length(self.o, self.a) - Length(self.o, self.c), Angle(self.b, self.o, self.m) + Angle(self.b, self.a, self.c) - pi, *Different(self.o, self.a, self.b, self.c, self.m), OppositeSide(self.a, self.o, self.b, self.c), Between(self.m, self.b, self.c)

    def conclusion(self):
        return Midpoint(self.m, self.b, self.c), Angle(self.c, self.o, self.m) + Angle(self.b, self.a, self.c) - pi, Perpendicular(self.o, self.m, self.b, self.c), Congruent3(self.o, self.m, self.b, self.o, self.m, self.c)


@register("basic")
class AlphaGeometry20(InferenceRule):
    """ Inversed Thales Theorem """
    def __init__(self, a: Point, b: Point, c: Point, m: Point):
        super().__init__()
        self.a = a
        self.b = b
        self.c = c
        self.m = m

    def condition(self):
        return Midpoint(self.m, self.a, self.c), Perpendicular(self.a, self.b, self.b, self.c), Lt(self.a, self.c)

    def conclusion(self):
        return equal(Length(self.a, self.m), Length(self.b, self.m), Length(self.c, self.m))
    
@register("basic")
class InversedThales2(InferenceRule):
    def __init__(self, o: Point, a: Point, b: Point, c: Point):
        super().__init__()
        self.o = o
        self.a = a
        self.b = b
        self.c = c

    def condition(self):
        return Perpendicular(self.a, self.b, self.b, self.c), Lt(self.a, self.c), Length(self.o, self.a) - Length(self.o, self.b), Length(self.o, self.a) - Length(self.o, self.c)

    def conclusion(self):
        return Collinear(self.a, self.c, self.o), Midpoint(self.o, self.a, self.c)


@register("basic")
class AlphaGeometry21(InferenceRule):
    """ Thales Theorem """
    def __init__(self, o: Point, a: Point, b: Point, c: Point):
        super().__init__()
        self.o = o
        self.a = a
        self.b = b
        self.c = c

    def condition(self):
        return Collinear(self.a, self.o, self.c), Not(Collinear(self.c, self.b, self.a)), Length(self.o, self.a) - Length(self.o, self.b), Length(self.o, self.a) - Length(self.o, self.c), Lt(self.a, self.c)

    def conclusion(self):
        return Perpendicular(self.a, self.b, self.b, self.c)


@register("basic")
class AlphaGeometry22(InferenceRule):
    """ Parallel lines intersect a circle forming a isosceles trapezoid """
    def __init__(self, a: Point, b: Point, c: Point, d: Point):
        super().__init__()
        self.a = a
        self.b = b
        self.c = c
        self.d = d

    def condition(self):
        return Concyclic(self.a, self.b, self.c, self.d), Parallel(self.a, self.b, self.c, self.d), Lt(self.a, self.b), Lt(self.c, self.d), Lt(self.a, self.c)

    def conclusion(self):
        return Angle(self.a, self.d, self.c)-Angle(self.d, self.c, self.b), Angle(self.b, self.a, self.d)-Angle(self.a, self.b, self.c)


@register("basic")
class AlphaGeometry23(InferenceRule):
    """ Points on the Perpendicular bisector are Equidistant from Segment Endpoints """
    def __init__(self, m: Point, o: Point, a: Point, b: Point):
        super().__init__()
        self.m = m
        self.o = o
        self.a = a
        self.b = b

    def condition(self):
        return Midpoint(self.m, self.a, self.b), Perpendicular(self.o, self.m, self.a, self.b), Lt(self.a, self.b)

    def conclusion(self):
        return Length(self.o, self.a)-Length(self.o, self.b), Congruent3(self.o, self.m, self.b, self.o, self.m, self.b)


@register("basic")
class AlphaGeometry24(InferenceRule):
    """ Points Equidistant from Segment Endpoints Determine its Perpendicular bisector """
    def __init__(self, a: Point, b: Point, p: Point, q: Point):
        super().__init__()
        self.a = a
        self.b = b
        self.p = p
        self.q = q

    def condition(self):
        return Length(self.a, self.p)-Length(self.b, self.p), Length(self.a, self.q)-Length(self.b, self.q), *Different(self.a, self.b, self.p, self.q), Lt(self.a, self.b), Lt(self.p, self.q)

    def conclusion(self):
        return Perpendicular(self.a, self.b, self.p, self.q), Congruent3(self.p, self.q, self.a, self.p, self.q, self.b)


@register("basic")
class AlphaGeometry25(InferenceRule):
    """ Perpendicular bisector intersecting a circle forming a kite """
    def __init__(self, a: Point, b: Point, p: Point, q: Point):
        super().__init__()
        self.a = a
        self.b = b
        self.p = p
        self.q = q

    def condition(self):
        return Concyclic(self.a, self.b, self.p, self.q), Length(self.a, self.p)-Length(self.b, self.p), Length(self.a, self.q)-Length(self.b, self.q), Lt(self.p, self.q), Lt(self.a, self.b)

    def conclusion(self):
        return Perpendicular(self.p, self.a, self.a, self.q), Perpendicular(self.p, self.b, self.b, self.q)


@register("basic")
class AlphaGeometry26(InferenceRule):
    """ If a point a the midpoint of two segments, the endpoints form a parallelogram """
    def __init__(self, a: Point, b: Point, c: Point, d: Point, m: Point):
        super().__init__()
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        self.m = m

    def condition(self):
        return Midpoint(self.m, self.a, self.b), Midpoint(self.m, self.c, self.d), Lt(self.a, self.b), Lt(self.c, self.d), Lt(self.a, self.c), *Different(self.a, self.b, self.c, self.d, self.m), Not(Collinear(self.a, self.b, self.c))

    def conclusion(self):
        return Parallel(self.a, self.c, self.b, self.d), Parallel(self.a, self.d, self.b, self.c), Parallelogram(self.a, self.c, self.b, self.d)


@register("basic")
class AlphaGeometry27(InferenceRule):
    """ diagonals of a parallelogram share a midpoint """
    def __init__(self, a: Point, b: Point, c: Point, d: Point, m: Point):
        super().__init__()
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        self.m = m

    def condition(self):
        return Midpoint(self.m, self.a, self.b), Parallel(self.a, self.c, self.b, self.d), Parallel(self.a, self.d, self.b, self.c), Lt(self.a, self.b), Lt(self.c, self.d), Not(Collinear(self.a, self.b, self.c)),  Not(Collinear(self.a, self.b, self.d)), Not(Collinear(self.a, self.c, self.d)), Not(Collinear(self.b, self.c, self.d))

    def conclusion(self):
        return Midpoint(self.m, self.c, self.d)


@register("basic")
class AlphaGeometry28(InferenceRule):
    """ inversed basic proportionality theorem """
    def __init__(self, a: Point, b: Point, c: Point, d: Point, o: Point):
        super().__init__()
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        self.o = o

    def condition(self):
        return Collinear(self.o, self.a, self.c), Collinear(self.o, self.b, self.d), Length(self.o, self.a)/Length(self.a, self.c)-Length(self.o, self.b)/Length(self.b, self.d), SameSide(self.c, self.d, self.a, self.b), SameSide(self.a, self.b, self.c, self.d), *Different(self.a, self.b, self.c, self.d, self.o), Lt(self.a, self.b)

    def conclusion(self):
        return Parallel(self.a, self.b, self.c, self.d)


@register("basic")
class AlphaGeometry29(InferenceRule):
    """ Parallel lines sharing a point are collinear """
    def __init__(self, a: Point, b: Point, c: Point):
        super().__init__()
        self.a = a
        self.b = b
        self.c = c

    def condition(self):
        return Parallel(self.a, self.b, self.a, self.c), *Different(self.a, self.b, self.c), Lt(self.b, self.c)

    def conclusion(self):
        return Collinear(self.a, self.b, self.c)


@register("basic")
class AlphaGeometry34(InferenceRule):  # SAS
    """ Triangle Congruence via SAS """
    def __init__(self, a: Point, b: Point, c: Point, p: Point, q: Point, r: Point):
        super().__init__()
        self.a = a
        self.b = b
        self.c = c
        self.p = p
        self.q = q
        self.r = r

    def condition(self):
        return Not(Collinear(self.a, self.b, self.c)), Length(self.a, self.b)-Length(self.p, self.q), Length(self.b, self.c)-Length(self.q, self.r), Angle(self.a, self.b, self.c) - Angle(self.p, self.q, self.r), Lt(self.a, self.c), Leq(self.b, self.q)

    def degenerate(self):
        return self.a == self.p and self.b == self.q and self.c == self.r

    def conclusion(self):
        return Congruent(self.a, self.b, self.c, self.p, self.q, self.r),


# @register("basic")
# class HLCongruent(InferenceRule):
#   def __init__(self, a: Point, b: Point, c: Point, p: Point, q: Point, r: Point):
#     super().__init__()
#     self.a = a
#     self.b = b
#     self.c = c
#     self.p = p
#     self.q = q
#     self.r = r

#   def condition(self):
#     return Not(Collinear(self.a,self.b,self.c)), Angle(self.a,self.b,self.c)-pi/2,Angle(self.p,self.q,self.r)-pi/2, Length(self.a,self.b)-Length(self.p,self.q), Length(self.a,self.c) - Length(self.p,self.r), Lt(self.a,self.c), Lt(self.a,self.p)

#   def degenerate(self):
#     return self.a==self.p and self.b == self.q and self.c == self.r

#   def conclusion(self):
#     return [Congruent(self.a,self.b,self.c,self.p,self.q,self.r)]


@register("basic")
class AlphaGeometry3536(InferenceRule):
    """ Similar Triangle via Equal angles """
    def __init__(self, a: Point, b: Point, c: Point, p: Point, q: Point, r: Point):
        super().__init__()
        self.a = a
        self.b = b
        self.c = c
        self.p = p
        self.q = q
        self.r = r

    def condition(self):
        return Not(Collinear(self.a, self.b, self.c)), Angle(self.a, self.b, self.c) - Angle(self.p, self.q, self.r), Angle(self.a, self.c, self.b) - Angle(self.p, self.r, self.q), Lt(self.a, self.b), Lt(self.b, self.c), Leq(self.a, self.p)

    def degenerate(self):
        return self.a == self.p and self.b == self.q and self.c == self.r

    def conclusion(self):
        return [Similar(self.a, self.b, self.c, self.p, self.q, self.r)]
    

@register("basic")
class SSS(InferenceRule):
    """ Triangle Congruence via SSS """
    def __init__(self, a: Point, b: Point, c: Point, p: Point, q: Point, r: Point):
        super().__init__()
        self.a = a
        self.b = b
        self.c = c
        self.p = p
        self.q = q
        self.r = r

    def condition(self):
        return Not(Collinear(self.a, self.b, self.c)), Length(self.a, self.b) - Length(self.p, self.q), Length(self.b, self.c)-Length(self.q, self.r), Length(self.c, self.a)-Length(self.r, self.p), Lt(self.a, self.b), Lt(self.b, self.c), Leq(self.a, self.p)

    def degenerate(self):
        return self.a == self.p and self.b == self.q and self.c == self.r

    def conclusion(self):
        return [Congruent(self.a, self.b, self.c, self.p, self.q, self.r)]


@register("basic")
class AlphaGeometry37(InferenceRule):
    """ Triangle Congruence via ASA """
    def __init__(self, a: Point, b: Point, c: Point, p: Point, q: Point, r: Point):
        super().__init__()
        self.a = a
        self.b = b
        self.c = c
        self.p = p
        self.q = q
        self.r = r

    def condition(self):
        return Not(Collinear(self.a, self.b, self.c)), Angle(self.a, self.b, self.c) - Angle(self.p, self.q, self.r), Angle(self.a, self.c, self.b) - Angle(self.p, self.r, self.q), Length(self.b, self.c)-Length(self.q, self.r), Lt(self.b, self.c), Leq(self.a, self.p)

    def degenerate(self):
        return self.a == self.p and self.b == self.q and self.c == self.r

    def conclusion(self):
        return [Congruent(self.a, self.b, self.c, self.p, self.q, self.r)]


@register("basic")
class AlphaGeometry38(InferenceRule):
    """ Triangle Congruence via AAS """
    def __init__(self, a: Point, b: Point, c: Point, p: Point, q: Point, r: Point):
        super().__init__()
        self.a = a
        self.b = b
        self.c = c
        self.p = p
        self.q = q
        self.r = r

    def condition(self):
        return Not(Collinear(self.a, self.b, self.c)), Angle(self.a, self.b, self.c) - Angle(self.p, self.q, self.r), Angle(self.b, self.a, self.c) - Angle(self.q, self.p, self.r), Length(self.b, self.c)-Length(self.q, self.r), Lt(self.b, self.c), Leq(self.a, self.p)

    def degenerate(self):
        return self.a == self.p and self.b == self.q and self.c == self.r

    def conclusion(self):
        return [Congruent(self.a, self.b, self.c, self.p, self.q, self.r)]


@register("basic")
class RTSSA(InferenceRule):
    """ Hypotenuse-Leg (HL) congruence criterion for right triangles """
    def __init__(self, a: Point, b: Point, c: Point, p: Point, q: Point, r: Point):
        super().__init__()
        self.a = a
        self.b = b
        self.c = c
        self.p = p
        self.q = q
        self.r = r

    def condition(self):
        return Not(Collinear(self.a, self.b, self.c)), Angle(self.a, self.b, self.c) - pi/2, Angle(self.p, self.q, self.r)-pi/2, Length(self.a, self.b)-Length(self.p, self.q), Length(self.a, self.c)-Length(self.p, self.r), Lt(self.a, self.c), Leq(self.b, self.q)

    def degenerate(self):
        return self.a == self.p and self.b == self.q and self.c == self.r

    def conclusion(self):
        return [Congruent(self.a, self.b, self.c, self.p, self.q, self.r)]


@register("basic")
class AlphaGeometry40(InferenceRule):
    """ Similar triangle via equal angle and length ratio """
    def __init__(self, a: Point, b: Point, c: Point, p: Point, q: Point, r: Point):
        super().__init__()
        self.a = a
        self.b = b
        self.c = c
        self.p = p
        self.q = q
        self.r = r

    def condition(self):
        return Not(Collinear(self.a, self.b, self.c)), Length(self.a, self.b)/Length(self.p, self.q)-Length(self.b, self.c)/Length(self.q, self.r), Angle(self.a, self.b, self.c) - Angle(self.p, self.q, self.r), Lt(self.a, self.c), Leq(self.b, self.q)

    def degenerate(self):
        return self.a == self.p and self.b == self.q and self.c == self.r

    def conclusion(self):
        return [Similar(self.a, self.b, self.c, self.p, self.q, self.r)]


@register("basic")
class AlphaGeometry42(InferenceRule):
    """ inversed basic proportionality theorem """
    def __init__(self, a: Point, b: Point, c: Point, d: Point, m: Point, n: Point):
        super().__init__()
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        self.m = m
        self.n = n

    def condition(self):
        return Collinear(self.m, self.a, self.d), Parallel(self.a, self.b, self.c, self.d), Collinear(self.n, self.b, self.c), Length(self.m, self.a)/Length(self.m, self.d)-Length(self.n, self.b)/Length(self.n, self.c),  SameSide(self.m, self.n, self.a, self.b),  SameSide(self.m, self.n, self.c, self.d), *Different(self.a, self.b, self.c, self.d), Lt(self.a, self.b), Lt(self.a, self.d)

    def conclusion(self):
        return Parallel(self.m, self.n, self.a, self.b)


@register("basic")
class AlphaGeometry43(InferenceRule):
    """ The basic proportionality theorem """
    def __init__(self, a: Point, b: Point, c: Point, d: Point, m: Point, n: Point):
        super().__init__()
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        self.m = m
        self.n = n

    def condition(self):
        return Collinear(self.m, self.a, self.d), Collinear(self.n, self.b, self.c), Parallel(self.a, self.b, self.m, self.n), Parallel(self.a, self.b, self.d, self.c), *Different(self.a, self.b, self.c, self.d, self.m, self.n), Lt(self.a, self.b), Lt(self.a, self.d), Lt(self.d, self.m), Not(Collinear(self.m, self.n, self.a)), Not(Collinear(self.m, self.n, self.d))

    def conclusion(self):
        return Length(self.m, self.a)/Length(self.m, self.d)-Length(self.n, self.b)/Length(self.n, self.c)


@register("basic")
class EqTrapezoid1(InferenceRule):
    def __init__(self, a: Point, b: Point, c: Point, d: Point):
        super().__init__()
        self.a = a
        self.b = b
        self.c = c
        self.d = d

    def condition(self):
        return (
            Parallel(self.a, self.b, self.c, self.d),
            SameSide(self.a, self.d, self.b, self.c),
            Length(self.a, self.c) - Length(self.b, self.d),  # diagonals
            *Different(self.a, self.b, self.c, self.d),
            Lt(self.a, self.b),
            Lt(self.a, self.c),
            Lt(self.a, self.d)
        )

    def conclusion(self):
        return Length(self.b, self.c) - Length(self.a, self.d), Angle(self.a, self.b, self.c) - Angle(self.b, self.a, self.d), Angle(self.b, self.a, self.c) - Angle(self.a, self.b, self.d)


@register("basic")
class EqTrapezoid2(InferenceRule):
    def __init__(self, a: Point, b: Point, c: Point, d: Point):
        super().__init__()
        self.a = a
        self.b = b
        self.c = c
        self.d = d

    def condition(self):
        return (
            Parallel(self.a, self.b, self.c, self.d),
            SameSide(self.a, self.d, self.b, self.c),
            Angle(self.a, self.b, self.c) - Angle(self.b, self.a, self.d),
            *Different(self.a, self.b, self.c, self.d),
            Lt(self.a, self.b),
            Lt(self.a, self.c),
            Lt(self.a, self.d)
        )

    def conclusion(self):
        return Length(self.a, self.c) - Length(self.b, self.d), Length(self.b, self.c) - Length(self.a, self.d), Angle(self.b, self.a, self.c) - Angle(self.a, self.b, self.d)


@register("basic")
class EqTrapezoid3(InferenceRule):
    def __init__(self, a: Point, b: Point, c: Point, d: Point):
        super().__init__()
        self.a = a
        self.b = b
        self.c = c
        self.d = d

    def condition(self):
        return (
            Parallel(self.a, self.b, self.c, self.d),
            SameSide(self.a, self.d, self.b, self.c),
            Angle(self.b, self.a, self.c) - Angle(self.a, self.b, self.d),
            *Different(self.a, self.b, self.c, self.d),
            Lt(self.a, self.b),
            Lt(self.a, self.c),
            Lt(self.a, self.d)
        )

    def conclusion(self):
        return Length(self.a, self.c) - Length(self.b, self.d), Length(self.b, self.c) - Length(self.a, self.d), Angle(self.a, self.b, self.c) - Angle(self.b, self.a, self.d)

    

@register("ex")
class BetweenLength(InferenceRule):
    def __init__(self, a: Point, b: Point, c: Point):
        super().__init__()
        self.a = a
        self.b = b
        self.c = c

    def condition(self):
        return Between(self.b, self.a, self.c), Lt(self.a, self.c)

    def conclusion(self):
        return Length(self.a, self.b)+Length(self.b, self.c)-Length(self.a, self.c)


@register("basic")  # stronger than basic9
class Perp2Angle(InferenceRule):
    def __init__(self, a: Point, b: Point, c: Point):
        super().__init__()
        self.a = a
        self.b = b
        self.c = c

    def condition(self):
        return Perpendicular(self.a, self.b, self.b, self.c), Lt(self.a, self.c)

    def conclusion(self):
        return Angle(self.a, self.b, self.c) - pi/2


@register("basic")
class Perp2Angle2(InferenceRule):  # one point inside triangle
    def __init__(self, a: Point, b: Point, c: Point, d: Point):
        super().__init__()
        self.a = a
        self.b = b
        self.c = c
        self.d = d

    def condition(self):
        return Perpendicular(self.a, self.b, self.c, self.d), SameSide(self.a, self.b, self.c, self.d), OppositeSide(self.c, self.d, self.a, self.b), SameSide(self.b, self.c, self.a, self.d), SameSide(self.b, self.d, self.a, self.c), Lt(self.c, self.d)

    def conclusion(self):
        return Angle(self.b, self.a, self.d) + Angle(self.c, self.d, self.a) - pi/2, Angle(self.b, self.a, self.c) + Angle(self.d, self.c, self.a) - pi/2, Angle(self.a, self.b, self.c) - Angle(self.b, self.c, self.d) - pi/2, Angle(self.a, self.b, self.d) - Angle(self.c, self.d, self.b) - pi/2


@register("basic")
class Perp2Angle3(InferenceRule):  # segments cross
    def __init__(self, a: Point, b: Point, c: Point, d: Point):
        super().__init__()
        self.a = a
        self.b = b
        self.c = c
        self.d = d

    def condition(self):
        return Perpendicular(self.a, self.b, self.c, self.d), OppositeSide(self.a, self.b, self.c, self.d), OppositeSide(self.c, self.d, self.a, self.b), Lt(self.a, self.b), Lt(self.c, self.d), Lt(self.a, self.c)

    def conclusion(self):
        return Angle(self.b, self.a, self.d) + Angle(self.c, self.d, self.a) - pi/2, Angle(self.b, self.a, self.c) + Angle(self.d, self.c, self.a) - pi/2, Angle(self.b, self.c, self.d) + Angle(self.a, self.b, self.c) - pi/2, Angle(self.a, self.b, self.d) + Angle(self.c, self.d, self.b) - pi/2


@register("basic")
class Angle2Perp(InferenceRule):
    def __init__(self, a: Point, b: Point, c: Point):
        super().__init__()
        self.a = a
        self.b = b
        self.c = c

    def condition(self):
        return Angle(self.a, self.b, self.c) - pi/2

    def conclusion(self):
        return Perpendicular(self.a, self.b, self.b, self.c)


@register("basic")
class Angle2Perp2(InferenceRule):  # point b inside triangle
    def __init__(self, a: Point, b: Point, c: Point, d: Point):
        super().__init__()
        self.a = a
        self.b = b
        self.c = c
        self.d = d

    def condition(self):
        return SameSide(self.a, self.b, self.c, self.d), OppositeSide(self.c, self.d, self.a, self.b), SameSide(self.b, self.c, self.a, self.d), SameSide(self.b, self.d, self.a, self.c), Angle(self.b, self.a, self.c) + Angle(self.d, self.c, self.a) - pi/2

    def conclusion(self):
        return Perpendicular(self.a, self.b, self.c, self.d)


@register("basic")
class Angle2Perp3(InferenceRule):  # segments cross
    def __init__(self, a: Point, b: Point, c: Point, d: Point):
        super().__init__()
        self.a = a
        self.b = b
        self.c = c
        self.d = d

    def condition(self):
        return OppositeSide(self.a, self.b, self.c, self.d), OppositeSide(self.c, self.d, self.a, self.b), Lt(self.a, self.d), Angle(self.b, self.a, self.d) + Angle(self.c, self.d, self.a) - pi/2

    def conclusion(self):
        return Perpendicular(self.a, self.b, self.c, self.d)


@register("basic")
class Angle2Para(InferenceRule):
    def __init__(self, a: Point, b: Point, c: Point, d: Point):
        super().__init__()
        self.a = a
        self.b = b
        self.c = c
        self.d = d

    def condition(self):
        return Angle(self.b, self.a, self.c) + Angle(self.a, self.c, self.d) - pi, Not(Collinear(self.a, self.b, self.c)), SameSide(self.b, self.d, self.a, self.c), Lt(self.a, self.c)

    def conclusion(self):
        return Parallel(self.a, self.b, self.c, self.d)


@register("basic")
class Para2Angle(InferenceRule):
    def __init__(self, a: Point, b: Point, c: Point, d: Point):
        super().__init__()
        self.a = a
        self.b = b
        self.c = c
        self.d = d

    def condition(self):
        return Parallel(self.a, self.b, self.c, self.d), Not(Collinear(self.a, self.b, self.c)), SameSide(self.b, self.d, self.a, self.c), Lt(self.a, self.c)

    def conclusion(self):
        return Angle(self.b, self.a, self.c) + Angle(self.a, self.c, self.d) - pi


@register("ex")
class DiagramAngle4a(InferenceRule):  # systemE Diagram-angle transfer 4
    def __init__(self, a: Point, b: Point, c: Point, b1: Point, c1: Point):
        super().__init__()
        self.a = a
        self.b = b
        self.c = c
        self.b1 = b1
        self.c1 = c1

    def condition(self):
        return Not(Between(self.a, self.c1, self.c)), Not(Between(self.a, self.b1, self.b)), *Different(self.a, self.b, self.c, self.b1, self.c1), Not(Collinear(self.a, self.b, self.c)), Collinear(self.a, self.c, self.c1), Collinear(self.b, self.b1, self.a)

    def conclusion(self):
        return Angle(self.b1, self.a, self.c1) - Angle(self.b, self.a, self.c)


@register("ex")
class DiagramAngle4b(InferenceRule):  # systemE Diagram-angle transfer 4
    def __init__(self, a: Point, b: Point, c: Point, b1: Point):
        super().__init__()
        self.a = a
        self.b = b
        self.c = c
        self.b1 = b1

    def condition(self):
        return Not(Between(self.a, self.b1, self.b)), *Different(self.a, self.b, self.c), *Different(self.a, self.b, self.c, self.b1), Not(Collinear(self.a, self.b, self.c)), Collinear(self.b, self.b1, self.a)

    def conclusion(self):
        return Angle(self.b1, self.a, self.c) - Angle(self.b, self.a, self.c)


@register("ex")
# systemE Diagram-angle transfer 2, Angle addition, stronger than basic10
class DiagramAngle2(InferenceRule):
    def __init__(self, a: Point, b: Point, c: Point, d: Point):
        super().__init__()
        self.a = a
        self.b = b
        self.c = c
        self.d = d

    def condition(self):
        return SameSide(self.b, self.d, self.c, self.a), SameSide(self.c, self.d, self.b, self.a), Lt(self.b, self.c)

    def conclusion(self):
        return Angle(self.b, self.a, self.c) - Angle(self.d, self.a, self.c) - Angle(self.d, self.a, self.b)

@register("ex")
class FlatAngle(InferenceRule):
    def __init__(self, a: Point, b: Point, c: Point):
        super().__init__()
        self.a = a
        self.b = b
        self.c = c

    def condition(self):
        return Collinear(self.a, self.b, self.c), Between(self.b, self.a, self.c), Lt(self.a, self.c)

    def conclusion(self):
        return Angle(self.a, self.b, self.c) - pi


@register("ex")
class FlatAngle2(InferenceRule):
    def __init__(self, a: Point, b: Point, c: Point, d: Point):
        super().__init__()
        self.a = a
        self.b = b
        self.c = c
        self.d = d

    def condition(self):
        return Collinear(self.a, self.b, self.c), Between(self.b, self.a, self.c), Lt(self.a, self.c), Not(Collinear(self.d, self.a, self.c)), *Different(self.a, self.b, self.c, self.d)

    def conclusion(self):
        return Angle(self.a, self.b, self.d) + Angle(self.c, self.b, self.d) - pi


@register("basic")
class FlatAngle2Collinear(InferenceRule):
    def __init__(self, a: Point, b: Point, c: Point):
        super().__init__()
        self.a = a
        self.b = b
        self.c = c

    def condition(self):
        return Angle(self.a, self.b, self.c) - pi, Lt(self.a, self.c)

    def conclusion(self):
        return Collinear(self.a, self.b, self.c)


@register("basic")
class ParaTrans(InferenceRule):
    def __init__(self, a: Point, b: Point, c: Point, d: Point, e: Point, f: Point):
        super().__init__()
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        self.e = e
        self.f = f

    def condition(self):
        return Parallel(self.a, self.b, self.c, self.d), Parallel(self.a, self.b, self.e, self.f), Lt(self.a, self.b), Lt(self.c, self.d), Lt(self.e, self.f), Lt(self.c, self.e), *Different(self.a, self.b, self.c), *Different(self.a, self.b, self.e)

    def degenerate(self):
        return self.a == self.c and self.b == self.d or self.a == self.e and self.b == self.f or self.e == self.c and self.f == self.d

    def conclusion(self):
        return Parallel(self.c, self.d, self.e, self.f)


@register("basic")
class CollinearParallel(InferenceRule):
    def __init__(self, a: Point, b: Point, c: Point):
        super().__init__()
        self.a = a
        self.b = b
        self.c = c

    def condition(self):
        return Collinear(self.a, self.b, self.c), Lt(self.a, self.b), Lt(self.b, self.c)

    def conclusion(self):
        return Parallel(self.a, self.b, self.b, self.c), Parallel(self.a, self.b, self.a, self.c), Parallel(self.a, self.c, self.b, self.c)