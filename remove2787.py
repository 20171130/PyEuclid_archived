import re

def extract_balanced_items(code_block):
    """
    Extract items like SameSide(...), OppositeSide(...), NotCollinear(...)
    with balanced parentheses.
    """
    items = []
    i = 0
    while i < len(code_block):
        match = re.match(r"(SameSide|OppositeSide|NotCollinear)\(", code_block[i:])
        if match:
            start = i + match.start()
            func_name = match.group(1)
            i = start + len(func_name) + 1  # skip past "FuncName("
            level = 1
            while i < len(code_block) and level > 0:
                if code_block[i] == '(':
                    level += 1
                elif code_block[i] == ')':
                    level -= 1
                i += 1
            item = code_block[start:i]
            items.append(item)
        else:
            i += 1
    return items

with open('data/Geometry3K/2787/problem.py', 'r') as f:
    code = f.read()

# Extract the diagrammatic_relations = [...] section
match = re.search(r"diagrammatic_relations\s*=\s*\[(.*?)]", code, re.DOTALL)
if match:
    content_inside = match.group(1)
    items = extract_balanced_items(content_inside)
    filtered = [item for item in items if "Point('T')" not in item]
    result = "diagrammatic_relations = [" + ", ".join(filtered) + "]"
    print(result)
else:
    print("No diagrammatic_relations list found.")
