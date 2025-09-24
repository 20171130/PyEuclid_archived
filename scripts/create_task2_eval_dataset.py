#!/usr/bin/env python3
import json
import argparse
from pathlib import Path
from tqdm import tqdm
import shutil

def main():
    ap = argparse.ArgumentParser(description="Build Alpaca VLM dataset with centralized images folder.")
    ap.add_argument("--dataset_dir", type=Path, default=Path("task2/proving_921_eval1_llm"),
                    help="Root containing *data.json + diagram.jpg pairs.")
    ap.add_argument("--out_json", type=Path, default=Path("data/task2/proving_921_eval1_llm/data.json"),
                    help="Output JSON path.")
    ap.add_argument("--images_dir", type=Path, default=Path("data/task2/proving_921_eval1_llm/images"),
                    help="Directory where all images will be copied.")
    ap.add_argument("--start", type=int, default=0, help="Start index (inclusive) after sorting.")
    ap.add_argument("--end", type=int, default=None, help="End index (inclusive) after sorting. Default: last.")
    ap.add_argument("--abs_paths", action="store_true", help="Store absolute image paths.")
    args = ap.parse_args()

    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.images_dir.mkdir(parents=True, exist_ok=True)

    # Collect and sort pairs
    pairs = []
    for data_path in sorted(tqdm(args.dataset_dir.rglob("*data.json"))):
        img_path = data_path.parent / "diagram.jpg"
        pairs.append((data_path, img_path))

    total_all = len(pairs)
    if total_all == 0:
        print(f"[!] No pairs found under: {args.dataset_dir}")
        return

    # Normalize slice bounds (end is inclusive)
    start_index = max(0, args.start)
    end_index = (total_all - 1) if args.end is None else min(args.end, total_all - 1)

    if start_index > end_index:
        print(f"[!] Empty slice: start={start_index}, end={end_index}, total={total_all}")
        return

    pairs = pairs[start_index:end_index + 1]

    dataset = []
    bad_json, missing_images, missing_keys = [], [], []

    for idx, (data_path, img_path) in enumerate(tqdm(pairs, total=len(pairs), desc="Building (Alpaca)")):
        try:
            with data_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            bad_json.append(f"{data_path} :: {e}")
            continue

        if "refined_problem" not in data or "refined_proof" not in data:
            missing_keys.append(str(data_path))
            continue

        if not img_path.exists():
            missing_images.append(str(img_path))
            continue

        problem = data["refined_problem"]
        proof = data["refined_proof"]

        # Copy image to centralized folder
        new_img_name = f"{idx}.jpg"
        new_img_path = args.images_dir / new_img_name
        
        shutil.copy(img_path, new_img_path)
        img_ref = str(new_img_path.resolve()) if args.abs_paths else str(new_img_path)

        sample = {
            "index": idx,
            "instruction": f"<image>\n{problem}",
            "input": "",
            "output": proof,
            "images": [img_ref],
        }
        dataset.append(sample)

    # Write output JSON
    with args.out_json.open("w", encoding="utf-8") as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)

    # Summary
    print("\n=== Summary ===")
    print(f"Total found     : {total_all}")
    print(f"Start index     : {start_index}")
    print(f"End index       : {end_index}")
    print(f"Sliced count    : {len(pairs)}")
    print(f"Written samples : {len(dataset)}")
    print(f"Bad JSON        : {len(bad_json)}")
    print(f"Missing images  : {len(missing_images)}")
    print(f"Missing keys    : {len(missing_keys)}")
    if bad_json:
        print("\nBad JSON examples:")
        for e in bad_json[:5]:
            print(" -", e)

if __name__ == "__main__":
    main()
