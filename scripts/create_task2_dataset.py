import json
import os
from pathlib import Path
import shutil
import time
import tqdm
from collections import defaultdict
import tqdm

problems = defaultdict(list)
dataset_dir = Path("task2/proving")
data_json_list = []
image_file_list = []
for json_file in tqdm.tqdm(dataset_dir.rglob("*data.json")):
    with open(json_file, "r") as f:
        data = json.load(f)
    problem = data.get("problem")
    proof = data.get("proof")
    sample_dir = json_file.parent
    data_json_list.append(os.path.join(sample_dir, "data.json"))

dataset = list()
error_list = list()
total_num = len(data_json_list)
for data_json in data_json_list[:100]:
    try:
        with open(data_json, "r") as f:
            data = json.load(f)
    except:
        error_list.append(data_json)
    
    problem = data["problem"]
    goal = data["goal"]
    proof = data["proof"]
    # question = f"Problem: {problem}\nGoal: {goal}\n"
    new_data = {
        "problem": problem,
        "goal": goal,
        "proof": proof
    }
    dataset.append(new_data)

print(f'Totoal: {len(dataset)} instances.')

with open(f"data/task2_samples.json", "w") as f:
    json.dump(dataset, f, indent=4)
