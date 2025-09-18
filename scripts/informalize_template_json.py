import json
import os
import shutil
from pathlib import Path
from pyeuclid.informalization.informalize_utils import *

# dataset_dir = "synthetic_dataset_0"
# dst_dataset_dir = "informalized_dataset"
# data_json_list = []
# image_file_list = []
# for entry in Path(dataset_dir).rglob("*data.json"):
#     sample_dir = entry.parent
#     data_json_list.append(os.path.join(sample_dir, "data.json"))
#     image_file_list.append(os.path.join(sample_dir, "diagram.jpg"))
# print("begin")

with open("data/task2_samples.json", "r") as f:
    data_list = json.load(f)
print(data_list)

# data_json_list = ["synthetic_dataset_0/rank_4/problem_0/sample_0/data.json"]
# image_file_list = ["synthetic_dataset_0/rank_4/problem_0/sample_0/diagram.jpg"]
# data_json_list = ["auxiliary_dataset/rank_12/problem_2/sample_0/data.json"]
# image_file_list = ["auxiliary_dataset/rank_12/problem_2/sample_0/diagram.jpg"]
total_num = len(data_list)
error_list = list()
result = dict()

for idx, data in enumerate(data_list):
    print(f"{idx + 1}/{total_num}")
    problem = data["problem"]
    goal = data["goal"]
    aux = ""
    proof = data["proof"]

    informal_problem = informalize_problem(problem)
    data["informal_problem"] = informal_problem
    # print(informal_problem)

    informal_goal = informalize_goal(goal)
    data["informal_goal"] = informal_goal
    # print(informal_goal)

    informal_aux = informalize_aux(aux)
    data["informal_aux"] = informal_aux
    # print(informal_aux)
    
    informal_proof = informalize_proof(proof)
    data["informal_proof"] = informal_aux + informal_proof
    print(informal_proof)
    
    if idx >= 10 : break

with open("data/informal_task2_samples.json", "w") as f:
    json.dump(data_list, f, indent=4)
