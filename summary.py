import argparse
from pathlib import Path
from typing import Tuple


def count_proof_files(
    results_dir: str,
    start: int = 1,
    end: int = 231,
    model_name: str | None = None,
) -> Tuple[int, int]:
    """
    Count how many problems are solved by checking proof files.

    If model_name is provided, also count <model_name>_proof.txt files.
    """
    base_path = Path(results_dir)
    total = end - start + 1
    proved = 0

    for idx in range(start, end + 1):
        subdir = base_path / str(idx)
        candidates = [subdir / "proof.txt"]
        if model_name:
            candidates.append(subdir / f"{model_name}_proof.txt")

        if any(p.is_file() for p in candidates):
            proved += 1
        
        if candidates[-1].is_file():
            print(candidates[-1])

    return proved, total


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("results_dir", type=str, help="Directory containing proof subfolders")
    parser.add_argument("--start", type=int, default=1, help="Start index of problems")
    parser.add_argument("--end", type=int, default=231, help="End index of problems")
    parser.add_argument("--model-name", type=str, default=None, help="Optional model name to check for *_proof.txt")

    args = parser.parse_args()

    proved, total = count_proof_files(args.results_dir, start=args.start, end=args.end, model_name=args.model_name)
    print(f"Successfully proved {proved} out of {total}.")
