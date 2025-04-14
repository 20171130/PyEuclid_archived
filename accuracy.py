import json
import jsonlines

# Load solved problems from old.jsonl


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
solved_new_file, status_map_new = load_solved_problems("new_results.jsonl")
load_error_problems("new_results.jsonl")
# load_error_problems("results.jsonl")
# Union accuracy
print(f"Total solved count: {len(solved_new_file)}")


