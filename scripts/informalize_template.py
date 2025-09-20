import json
import os
import shutil
from pathlib import Path
from pyeuclid.informalization.informalize_utils import *
import tqdm

dataset_dir = "task2/proving_918"
dst_dataset_dir = "task2/proving_918_template"
data_json_list = []
image_file_list = []
for entry in tqdm.tqdm(Path(dataset_dir).rglob("*data.json")):
    sample_dir = entry.parent
    data_json_list.append(os.path.join(sample_dir, "data.json"))
    image_file_list.append(os.path.join(sample_dir, "diagram.jpg"))
print("begin")

total_num = len(data_json_list)
error_list = list()
result = dict()

for idx, (data_json, image_file) in tqdm.tqdm(enumerate(zip(data_json_list, image_file_list))):
    try:
        with open(data_json, "r") as f:
            data = json.load(f)
    except:
        error_list.append(data_json)
        continue
    problem = data["problem"]
    goal = data["goal"]
    proof = data["proof"]

    informal_problem = informalize_problem(problem)
    data["informal_problem"] = informal_problem

    informal_goal = informalize_goal(goal)
    data["informal_goal"] = informal_goal
    
    informal_proof = informalize_proof(proof)
    data["informal_proof"] = informal_proof

    dst_data_json = data_json.replace(dataset_dir, dst_dataset_dir)
    dst_image_file = image_file.replace(dataset_dir, dst_dataset_dir)
    os.makedirs(os.path.dirname(dst_data_json), exist_ok=True)
    with open(dst_data_json, "w") as f:
        json.dump(data, f, indent=4)
    # if os.path.islink(dst_image_file):
    #     os.unlink(dst_image_file)
    # elif os.path.exists(dst_image_file):
    #     os.remove(dst_image_file)
    # os.symlink(os.path.abspath(image_file), dst_image_file)

    if os.path.exists(dst_image_file):
        os.remove(dst_image_file)
    shutil.copy2(image_file, dst_image_file)

print(error_list)