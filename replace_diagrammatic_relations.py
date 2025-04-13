import os
import re

def extract_rhs(full_text, keyword):
    """
    Extract the full right-hand side of an assignment like:
    keyword = set(...)
    keyword = {...}
    keyword = [...]
    keyword = set()
    """
    pattern = rf"{keyword}\s*=\s*(.*)"
    match = re.search(pattern, full_text)
    if not match:
        return None

    rhs = match.group(1).strip()

    if rhs.startswith(("set(", "list(")):
        # Handle function-style: set(...) or list(...)
        open_paren = rhs.find("(")
        count = 1
        i = open_paren + 1
        while i < len(rhs):
            if rhs[i] == "(":
                count += 1
            elif rhs[i] == ")":
                count -= 1
                if count == 0:
                    return rhs[:i+1]
            i += 1
        return rhs  # fallback
    elif rhs.startswith(("{", "[")):
        # Handle bracket-style
        open_char = rhs[0]
        close_char = "]" if open_char == "[" else "}"
        count = 1
        i = 1
        while i < len(rhs):
            if rhs[i] == open_char:
                count += 1
            elif rhs[i] == close_char:
                count -= 1
                if count == 0:
                    return rhs[:i+1]
            i += 1
        return rhs  # fallback
    else:
        return rhs.splitlines()[0]  # fallback: handle cases like `= set()`

def process_file(filepath):
    with open(filepath, "r") as f:
        content = f.read()

    rhs_new = extract_rhs(content, "new_diagrammatic_relations")
    if rhs_new is None:
        print(f"[SKIP] new_diagrammatic_relations not found in {filepath}")
        return

    # Replace diagrammatic_relations = ... with diagrammatic_relations = <new_value>
    pattern_diag = r"(diagrammatic_relations\s*=\s*)([\s\S]*?)(?=\n\S|$)"
    if not re.search(pattern_diag, content):
        print(f"[SKIP] diagrammatic_relations not found in {filepath}")
        return

    content = re.sub(pattern_diag, rf"\1{rhs_new}", content)

    # Remove the new_diagrammatic_relations assignment entirely
    pattern_new = r"new_diagrammatic_relations\s*=\s*[\s\S]*?(?:\n{1,2})"
    content = re.sub(pattern_new, "", content)

    # Save to new file
    new_filepath = filepath.replace("problem.py", "problem_updated.py")
    with open(new_filepath, "w") as f:
        f.write(content)

    print(f"[OK] {new_filepath} updated.")


# Process all files
for i in range(2401, 3002):
    path = f"data/Geometry3K/{i}/problem.py"
    if os.path.isfile(path):
        process_file(path)
    else:
        print(f"[MISSING] {path}")
