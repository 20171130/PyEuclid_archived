import os
import re

for i in range(2401, 3002):
    input_path = f"intergps/{i}/readable_problem.py"
    output_path = f"data/Geometry3K/{i}/problem.py"

    if not os.path.exists(input_path) or not os.path.exists(output_path):
        continue

    with open(input_path, "r", encoding="utf-8") as f:
        content = f.read()

    match = re.search(r'(lines.*\n.*)', content, re.DOTALL)
    if match:
        lines_and_after = match.group(1)
        with open(output_path, "a", encoding="utf-8") as out:
            out.write("\n" + lines_and_after)
