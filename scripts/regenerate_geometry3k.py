import time
import logging
import argparse
import sympy
from itertools import combinations
import pyeuclid.formalization.utils as utils
from pyeuclid.formalization.state import State
from pyeuclid.formalization.relation import *
from pyeuclid.formalization.construction_rule import *
from pyeuclid.formalization.utils import *
from pyeuclid.engine.inference_rule import *
from pyeuclid.engine.deductive_database import DeductiveDatabase
from pyeuclid.engine.algebraic_system import AlgebraicSystem
from pyeuclid.engine.proof_generator import ProofGenerator
from pyeuclid.engine.engine import Engine
from typing import Iterable
import io

def _point_name(p):
    # Try common attributes; fall back to str(p)
    for attr in ("name", "label", "id"):
        if hasattr(p, attr):
            return str(getattr(p, attr))
    return str(p)

def _relation_to_code(rel):
    cls_name = rel.__class__.__name__
    if isinstance(rel, Collinear):
        cls_name = 'Not' + cls_name

    pts = rel.get_points()  # expected: iterable of Point objects
    pts_code = ", ".join(f"Point({_repr_point_name(_point_name(p))})" for p in pts)
    
    return f"{cls_name}({pts_code})"

def _repr_point_name(s: str) -> str:
    # Always single-quote, escaping any embedded quotes/backslashes
    return "'" + s.replace("\\", "\\\\").replace("'", "\\'") + "'"

def dump_relations_to_py(
    relations: Iterable,
    path: str,
    multiline: bool = True,
):
    # Build body
    items = [_relation_to_code(r) for r in relations]
    if multiline:
        body = ",\n    ".join(items)
        content = io.StringIO()
        content.write("\n\n")
        content.write("diagrammatic_relations = [\n")
        content.write("    " + body + "\n")
        content.write("]\n")
        text = content.getvalue()
    else:
        body = ", ".join(items)
        text = "\n".join(imports) + f"\n\ndiagrammatic_relations = [{body}]\n"

    with open(path, "w", encoding="utf-8") as f:
        f.write(text)

# problem = "K@-8.49_0.84 H@-1.39_3.59 J@-2.06_-1.56 = triangle K H J; A@-4.62_1.39 = free A; G@-8.33_2.61 = on_circle G A H; F@-11.87_2.11 = on_line F G H, on_line F K J"
problem = "R T S = triangle R T S; P = midpoint R S"
state = State()
state.load_problem_from_text(problem, f'diagrams/test.jpg', resample=True)
rs = []
for relation in state.relations:
    if isinstance(relation, (SameSide, OppositeSide, Between)):
        pts = relation.get_points()
        rs.append(relation)
    elif isinstance(relation, Collinear) and relation.negated:
        pts = relation.get_points()
        rs.append(relation)
print(rs)
dump_relations_to_py(rs, 'try.py')