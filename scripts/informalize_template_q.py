import json
import os
from pathlib import Path
import tqdm
import fitz  # PyMuPDF
from pyeuclid.informalization.informalize_utils import *
from concurrent.futures import ProcessPoolExecutor, as_completed

dataset_dir = "task1/calculation_921"
dst_dataset_dir = "task1/calculation_921_samples_template"
data_json_list = []
image_file_list = []

# collect all data.json + diagram.pdf pairs (cap to 100000 like your original)
for entry in sorted(tqdm.tqdm(Path(dataset_dir).rglob("*data.json"))):
    sample_dir = entry.parent
    data_json_list.append(os.path.join(sample_dir, "data.json"))
    image_file_list.append(os.path.join(sample_dir, "diagram.pdf"))

pairs = list(zip(data_json_list, image_file_list))
total_num = len(pairs)

def pdf_first_page_to_jpg(src_pdf: str, dst_jpg: str, dpi: int = 300):
    """Render the first page of a 1-page PDF to a JPEG using PyMuPDF."""
    os.makedirs(os.path.dirname(dst_jpg), exist_ok=True)
    # dpi -> zoom factor: 72 dpi is 1.0
    zoom = dpi / 72.0
    mat = fitz.Matrix(zoom, zoom)
    with fitz.open(src_pdf) as doc:
        if doc.page_count == 0:
            raise RuntimeError("Empty PDF")
        page = doc[0]
        pix = page.get_pixmap(matrix=mat, alpha=False)  # ensure no alpha for JPEG
        pix.save(dst_jpg, output="jpeg")  # explicitly write JPEG

def process_one(args):
    """
    Process a single (data_json, image_pdf) pair.
    Returns None on success, or a tuple (where, path, error_str) on failure.
    """
    data_json, image_file = args
    try:
        with open(data_json, "r") as f:
            data = json.load(f)
    except Exception as e:
        return ("read_json", data_json, str(e))

    # Extract required fields (fail fast if missing)
    try:
        problem = data["problem"]
        goal = data["goal"]
        proof = data["proof"]
    except Exception as e:
        return ("missing_fields", data_json, str(e))

    # Informalization (these may be I/O or CPU-bound; done inside the worker)
    try:
        informal_problem = informalize_problem_q(problem)
        data["informal_problem"] = informal_problem

        informal_goal = informalize_goal_q(goal)
        data["informal_goal"] = informal_goal

        informal_proof = informalize_proof_q(proof)
        data["informal_proof"] = informal_proof
    except Exception as e:
        return ("informalize", data_json, str(e))

    # Destination paths
    try:
        dst_data_json = data_json.replace(dataset_dir, dst_dataset_dir)
        dst_image_file = image_file.replace(dataset_dir, dst_dataset_dir).replace(".pdf", ".jpg")
        os.makedirs(os.path.dirname(dst_data_json), exist_ok=True)
    except Exception as e:
        return ("prepare_dst", data_json, str(e))

    # Write JSON
    try:
        with open(dst_data_json, "w") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        return ("write_json", dst_data_json, str(e))

    # PDF → JPG
    try:
        pdf_first_page_to_jpg(image_file, dst_image_file, dpi=300)
    except Exception as e:
        return ("pdf_to_jpg", image_file, str(e))

    return None  # success

# Choose worker count (override with env MAX_WORKERS)
max_workers = 60

error_list = []
if total_num == 0:
    print("No data found.")
else:
    # Use ProcessPoolExecutor so CPU-bound PDF rendering can scale
    with ProcessPoolExecutor(max_workers=max_workers) as ex:
        futures = [ex.submit(process_one, p) for p in pairs]
        for fut in tqdm.tqdm(as_completed(futures), total=total_num):
            err = fut.result()
            if err is not None:
                error_list.append(err)

print("Errors:", error_list)