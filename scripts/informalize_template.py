import json
import os
import shutil
from pathlib import Path
from pyeuclid.informalization.informalize_utils import *

dataset_dir = "synthetic_dataset_0"
dst_dataset_dir = "informalized_dataset"
data_json_list = []
image_file_list = []
for entry in Path(dataset_dir).rglob("*data.json"):
    sample_dir = entry.parent
    data_json_list.append(os.path.join(sample_dir, "data.json"))
    image_file_list.append(os.path.join(sample_dir, "diagram.jpg"))
print("begin")

# data_json_list = ["synthetic_dataset_0/rank_4/problem_0/sample_0/data.json"]
# image_file_list = ["synthetic_dataset_0/rank_4/problem_0/sample_0/diagram.jpg"]
# data_json_list = ["auxiliary_dataset/rank_12/problem_2/sample_0/data.json"]
# image_file_list = ["auxiliary_dataset/rank_12/problem_2/sample_0/diagram.jpg"]
total_num = len(data_json_list)
error_list = list()
result = dict()

for idx, (data_json, image_file) in enumerate(zip(data_json_list, image_file_list)):
    print(f"{idx + 1}/{total_num}")
    try:
        with open(data_json, "r") as f:
            data = json.load(f)
    except:
        error_list.append(data_json)
        continue
    problem = data["problem"]
    goal = data["goal"]
    aux = data["auxiliary_constructions"]
    proof = data["proof"]

    informal_problem = informalize_problem(problem)
    data["informal_problem"] = informal_problem
    # print(informal_problem)

    informal_goal = informalize_goal(goal)
    data["informal_goal"] = informal_goal
    # print(informal_goal)

    informal_aux = informalize_aux(aux)
    data["informal_aux"] = informal_aux
    print(informal_aux)
    
    informal_proof = informalize_proof(proof)
    data["informal_proof"] = informal_aux + informal_proof
    # print(informal_proof)

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

    # exit()

print(error_list)