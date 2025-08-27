import argparse
from pathlib import Path

def count_proof_files(results_dir: str, start: int = 1, end: int = 231) -> tuple[int, int]:
    base_path = Path(results_dir)
    total = end - start + 1   # total number of expected idx
    proved = 0
    for idx in range(start, end + 1):
        subdir = base_path / str(idx)
        proof_file = subdir / "proof.txt"   # or "proof.txt"
        if proof_file.is_file():
            proved += 1
    return proved, total


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "results_dir",
        type=str,
    )
    args = parser.parse_args()

    proved, total = count_proof_files(args.results_dir)
    print(f"Successfully proved {proved} out of {total}.")
