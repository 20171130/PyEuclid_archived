import json
import jsonlines

# Load solved problems from old.jsonl
old = set()
with jsonlines.open("old.jsonl") as reader:
    for obj in reader:
        if obj.get("status") == "solved":
            old.add(str(obj["problem_number"]))

# Function to load 'solved' problems from any results file
def load_solved_problems(filepath):
    solved = set()
    status_map = {}
    with jsonlines.open(filepath) as reader:
        for obj in reader:
            prob_id = str(obj.get("problem_number"))
            status = obj.get("status", "unknown")
            if status == "solved":
                solved.add(prob_id)
            status_map[prob_id] = status
    return solved, status_map

def load_error_problems(filepath):
    solved = set()
    status_map = {}
    with jsonlines.open(filepath) as reader:
        for obj in reader:
            prob_id = str(obj.get("problem_number"))
            status = obj.get("status", "unknown")
            if status == "error":
                print(prob_id)
                solved.add(prob_id)
            status_map[prob_id] = status
    return solved, status_map

# Load solved problems and full status maps
solved_old_file, status_map_old = load_solved_problems("results.jsonl")
solved_new_file, status_map_new = load_solved_problems("new_results.jsonl")
load_error_problems("new_results.jsonl")
# load_error_problems("results.jsonl")
# Union accuracy
solved_union = solved_old_file | solved_new_file
print(f"Total new solved count: {len(solved_new_file)}")
print(f"Total old solved count: {len(solved_old_file)}")

print(f"Total union solved count: {len(solved_union)}")

# Symmetric difference
solved_symmetric_diff = solved_old_file - solved_new_file
solved_symmetric_diff_sorted = sorted(solved_symmetric_diff, key=lambda x: int(x))
print(f"Problems solved by original only: {solved_symmetric_diff_sorted}")
solved_symmetric_diff = solved_new_file - solved_old_file 
solved_symmetric_diff_sorted = sorted(solved_symmetric_diff, key=lambda x: int(x))
print(f"Problems solved by new only: {solved_symmetric_diff_sorted}")

# Solved by union but NOT by old
union_not_old = sorted([pid for pid in solved_union if pid not in old], key=lambda x: int(x))
print(f"\nSolved by union but not by old system: {union_not_old}")

# Solved by old but NOT by union
old_not_union = sorted([pid for pid in old if pid not in solved_union], key=lambda x: int(x))
print(f"Solved by old system but not by union: {old_not_union}")

# Status for problems NOT solved by union
all_problem_ids = set(status_map_old) | set(status_map_new)
not_solved_by_union = sorted([pid for pid in all_problem_ids if pid not in solved_union], key=lambda x: int(x))

status_details = []
for pid in not_solved_by_union:
    status_old = status_map_old.get(pid)
    status_new = status_map_new.get(pid)
    status_combined = status_old if status_old in {"wrong", "unsolved"} else status_new
    status_details.append((pid, status_combined))

# print(f"\nProblems not solved by union and their status:")
# for pid, status in status_details:
#     print(f"{pid}: {status}")
