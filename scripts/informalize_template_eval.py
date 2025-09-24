import json
import os
import shutil
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
from pyeuclid.informalization.informalize_utils import (
    informalize_problem,
    informalize_goal,
    informalize_proof,
)
from tqdm import tqdm


dataset_dir = "task2/proving_921"
dst_dataset_dir = "task2/proving_921_eval1_template"
max_workers = os.cpu_count() or 32


def process_sample(data_json: str, image_file: str, dataset_dir: str, dst_dataset_dir: str):
    """
    Worker function: load JSON, informalize, write JSON + copy image.
    Returns None if success, or data_json path if failed.
    """
    try:
        with open(data_json, "r") as f:
            data = json.load(f)
    except Exception:
        return data_json  # error reading

    try:
        problem = data["problem"]
        goal = data["goal"]
        proof = data["proof"]

        data["informal_problem"] = informalize_problem(problem)
        data["informal_goal"] = informalize_goal(goal)
        data["informal_proof"] = informalize_proof(proof)

        dst_data_json = data_json.replace(dataset_dir, dst_dataset_dir)
        dst_image_file = image_file.replace(dataset_dir, dst_dataset_dir)
        os.makedirs(os.path.dirname(dst_data_json), exist_ok=True)

        with open(dst_data_json, "w") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        if os.path.exists(image_file):
            os.makedirs(os.path.dirname(dst_image_file), exist_ok=True)
            if os.path.exists(dst_image_file):
                os.remove(dst_image_file)
            shutil.copy2(image_file, dst_image_file)

        return None
    except Exception:
        return data_json


def main():
    data_json_list = []
    image_file_list = []

    ds_dir = Path(dataset_dir)
    all_entries = sorted(tqdm(ds_dir.rglob("*data.json")))[99000:100000]

    for entry in tqdm(all_entries, desc="Scanning", unit="file"):
        try:
            with open(entry, "r") as f:
                data = json.load(f)
        except Exception as e:
            # skip corrupted JSONs
            continue

        if data.get("depth", 9999) <= 3:
            sample_dir = entry.parent
            data_json_list.append(str(sample_dir / "data.json"))
            image_file_list.append(str(sample_dir / "diagram.jpg"))

            if len(data_json_list) >= 100:
                break

    print("begin")

    error_list = []

    with ProcessPoolExecutor(max_workers=max_workers) as ex:
        futures = [
            ex.submit(process_sample, dj, im, dataset_dir, dst_dataset_dir)
            for dj, im in zip(data_json_list, image_file_list)
        ]

        for future in tqdm(as_completed(futures), total=len(futures), desc="Processing"):
            res = future.result()
            if res is not None:
                error_list.append(res)

    print("Done.")
    if error_list:
        print("Errors:", error_list)


if __name__ == "__main__":
    main()