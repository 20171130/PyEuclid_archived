import sympy
from pyeuclid.formalization.relation import *


def generate_additional_props_from_readable(side_map):
    all_points = set()
    additional_relations = set()
    for i in side_map.keys():
        for j in i:
            if j not in all_points:
                all_points.add(j)
    
    for key,val in side_map.items():
        side1 = val[0]
        side2 = val[1]
        for i in key:
            for j in key:
                if i != j:
                    for k in side1:
                        for l in side1:
                            if k != l:
                                additional_relations.add(SameSide(Point(k),Point(l),Point(i),Point(j)))

                        for l in side2:
                            if k != l:
                                additional_relations.add(OppositeSide(Point(k),Point(l),Point(i),Point(j)))
                    for k in side2:
                        for l in side2:
                            if k != l:
                                additional_relations.add(SameSide(Point(k),Point(l),Point(i),Point(j)))

                        for l in side1:
                            if k != l:
                                additional_relations.add(OppositeSide(Point(k),Point(l),Point(i),Point(j)))
                    for k in all_points:

                        if k not in key:
                            additional_relations.add(NotCollinear(Point(i),Point(j),Point(k)))
    for key in side_map.keys():
        for i in range(len(key)):
            for j in range(i+1,len(key)):
                for k in range(j+1, len(key)):
                    additional_relations.add(Between(Point(key[j]),Point(key[i]),Point(key[k])))
    str_to_add = set()

    for i in additional_relations:
        if isinstance(i, Between):
            str_to_add.add(f"Between(Point('{i.p1}'),Point('{i.p2}'),Point('{i.p3}'))")
        if isinstance(i, NotCollinear):
            str_to_add.add(f"NotCollinear(Point('{i.p1}'),Point('{i.p2}'),Point('{i.p3}'))")
        if isinstance(i, SameSide):
            str_to_add.add(f"SameSide(Point('{i.p1}'),Point('{i.p2}'),Point('{i.p3}'),Point('{i.p4}'))")
        if isinstance(i, OppositeSide):
            str_to_add.add(f"OppositeSide(Point('{i.p1}'),Point('{i.p2}'),Point('{i.p3}'),Point('{i.p4}'))")
    str_to_add = str(str_to_add).replace('"','')
    return f"new_diagrammatic_relations = {str_to_add}"
    



import os
import re
import ast
from pathlib import Path

from pyeuclid.formalization.relation import *

def extract_lines_value(code):
    match = re.search(r'lines\s*=\s*({.*?})(?:\n|$)', code, flags=re.DOTALL)
    if not match:
        return None
    dict_str = match.group(1)
    return ast.literal_eval(dict_str)


def replace_lines_block(code, additional):
    # Match 'lines = {...}' or 'lines = [...]' and remove it
    pattern = r"lines\s*=\s*(\[.*?\]|\{.*?\})(\n|$)"
    return re.sub(pattern, additional + "\n", code, count=1, flags=re.DOTALL)


for i in range(2401, 3002):
    
    path = Path(f"data/Geometry3K/{i}/problem.py")
    if not path.exists():
        continue

    with open(path, "r", encoding="utf-8") as f:
        code = f.read()

    try:
        side_map = extract_lines_value(code)
        if side_map is None:
            print(f"Skipping {i}: 'lines' not found or invalid")
            continue

        # Call your function
        additional = generate_additional_props_from_readable(side_map)


        # Replace the old block
        new_code = replace_lines_block(code, additional)

        with open(path, "w", encoding="utf-8") as f:
            f.write(new_code)

        print(f"Updated: {i}")
    except Exception as e:
        print(f"Error processing {i}: {e}")
