import re
import json
with open('slurm-90334.out', 'r') as f:
    data = f.read()

# Extract 4-digit numbers from lines containing "solved"
matches = re.findall(r'^(\d{4}):.*solved', data, re.MULTILINE)

print("Solved IDs:", len(matches))
with open("old.jsonl", "w") as f:
    for problem_id in matches:
        json.dump({"problem_number": problem_id, "status": "solved"}, f)
        f.write("\n")