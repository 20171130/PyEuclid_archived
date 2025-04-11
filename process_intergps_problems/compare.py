import json
import jsonlines

# Load the JSON file
with open("old.json", "r") as f:
    solved_json = json.load(f)

solved_set = {int(k) for k, v in solved_json.items() if v.get("status") == "solved"}

# Load the JSONL file
success_set = set()
with jsonlines.open("geometry3k_status.jsonl") as reader:
    for obj in reader:
        if obj.get("status") == "success":
            success_set.add(obj["idx"])

# Compute differences
success_not_solved = sorted(success_set - solved_set)
solved_not_success = sorted(solved_set - success_set)

print("Failed by System E, succeeded by Pyeuclid", success_not_solved)
print("Failed by Pyeuclid, succeeded by System E", solved_not_success)
