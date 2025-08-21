import json
import os
from pathlib import Path
import shutil
import time
import tqdm

system_prompt = (
    "You are an expert in plane geometry, specializing in identifying the most effective "
    "auxiliary constructions for solving geometry problems. Given a formal geometry problem, "
    "output only the essential auxiliary constructions required for the solution. "
    "Use existing points as inputs and give unique names to all newly constructed points. "
    "Each new point must be defined using no more than two auxiliary constructions."
)


dataset_dir = Path("new_dataset")
data_json_list = []
image_file_list = []
for json_file in dataset_dir.rglob("*data.json"):
    with open(json_file, "r") as f:
        data = json.load(f)

    has_aux = data.get("has_auxiliary_constructions")
    sub_conclusion = data.get("sub_conclusion", None)

    if has_aux and sub_conclusion is False:
        sample_dir = json_file.parent
        data_json_list.append(os.path.join(sample_dir, "data.json"))

dataset = list()
error_list = list()
total_num = len(data_json_list)
for data_json in data_json_list:
    try:
        with open(data_json, "r") as f:
            data = json.load(f)
    except:
        error_list.append(data_json)
    
    problem = data["problem"]
    goal = data["goal"]
    auxiliary_constructions = data["auxiliary_constructions"]
    question = f"Problem: {problem}\nGoal: {goal}\n"
    answer = auxiliary_constructions
    new_data = {
        "system": system_prompt,
        "instruction": question,
        "input": "",
        "output": answer
    }
    dataset.append(new_data)

with open(f"data/pyeuclid_text_train.json", "w") as f:
    json.dump(dataset, f, indent=4)
