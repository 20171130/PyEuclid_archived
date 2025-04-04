import re
import os

def extract_points_from_code(code):
    """Extract all unique point names used in Point('X') throughout the code."""
    return set(re.findall(r"Point\('([A-Z])'\)", code))

def process_file(input_file, output_file):
    with open(input_file, 'r') as f:
        code = f.read()

    # 1. Replace imports
    code = re.sub(r"from euclid\.prop import \*\n?", "", code)
    code = re.sub(r"import sympy", "import sympy\n\nfrom pyeuclid.formalization.relation import *\n", code)

    # 2. Extract all used points
    used_points = extract_points_from_code(code)

    # 2. Clean the point declaration block
    point_decl_pattern = (
        r"(A,B,C,D,E,F,G,H,I,J,K,L,M,N,O,P,Q,R,S,T,U,V,W,X,Y,Z\s*=\s*"
        r"(?:Point\('[A-Z]'\),\s*){25}Point\('[A-Z]'\))"
    )
    match = re.search(point_decl_pattern, code)
    if match:
        # Build a new declaration line with only the used points
        all_points = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        new_decl = []
        for pt in all_points:
            if pt in used_points:
                new_decl.append(f"{pt} = Point('{pt}')")
        new_decl_code = ', '.join(new_decl)
        code = re.sub(point_decl_pattern, new_decl_code, code)

    # 3. Rename 'props' to 'relations'
    code = re.sub(r'\bprops\b', 'relations', code)

    # 4. Rename 'NColl' to 'NotCollinear'
    code = re.sub(r'\bNColl\b', 'NotCollinear', code)

    # Save the output
    with open(output_file, 'w') as f:
        f.write(code)

# Example usage
for idx in range(2494, 2495): # 2591, 2815
    # try:
    #     with open(f'{idx}/problem.py', 'r') as f:
    #         code = f.read()
    #     assert 'additional' in code
    # except:
    #     print(idx)
    # process_file(f"{idx}/problem.py", f"{idx}/problem.py")
    # os.remove(f"{idx}/readable_problem.py")
