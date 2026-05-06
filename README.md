# Euclid-Omni: A Unified Neuro-Symbolic Framework for Plane Geometry

Euclid-Omni couples a versatile symbolic plane-geometry solver, **Euclidea**, with Large Language Models and Vision-Language Models to tackle calculation- and proving-style problems up to Olympiad-level difficulty. Building on Euclidea, Euclid-Omni provides a synthetic problem generator, a diagram renderer, and a natural-language translator that together produce large-scale, diverse training data.

This repository contains the code and instructions to reproduce the experiments reported in our paper.

## Computational Resources

We evaluate the symbolic solver on a server running Ubuntu 22.04.5 LTS with an AMD Ryzen Threadripper 2990WX (30 CPU cores in parallel; 2 cores per process, 4 GB per process). With this setup, JGEX-AG-231 finishes in roughly 2 hours and Geometry3K in roughly 1 hour. Sequential runs on an Apple MacBook Pro M3 (2 CPU cores, 4 GB) take approximately 7-8 hours on Geometry3K.

For supervised fine-tuning we use 8&times;H100 GPUs: 3 epochs on 20K calculation examples for Qwen2.5-VL-7B (Section 5.2 of the paper), and 1 epoch on 100K proving examples for Qwen2.5-Math-7B (Section 5.3).

## Folder Structure

```
.
├── pyeuclid/
│   ├── engine/                 # Euclidea reasoning core: deductive database, algebraic system, proof generator
│   ├── formalization/          # Relations, construction rules, state, diagram, translation
│   └── informalization/        # Natural-language templates and LLM-based translation/refinement
├── scripts/                    # Data generation, training data assembly, and evaluation entry points
├── tests/                      # Single-problem and benchmark drivers (Geometry3K, JGEX-AG-231, IMO-AG-30)
├── data/                       # Benchmark inputs (JGEX-AG-231.txt, IMO-AG-30.txt, Geometry3K/, ...)
├── configs/train/              # LLaMA-Factory training configs for the calculation VLM and the proving LLM
├── visualization/              # Optional diagram-rendering web utilities
├── Dockerfile                  # Containerized setup
├── requirements.txt            # Python dependencies
├── setup.py                    # Package metadata
└── summary.py                  # Counts solved problems by inspecting result directories
```

## Installation

You can run Euclid-Omni inside Docker or in a local conda environment.

Docker:
```bash
docker build -t euclid-omni .
docker run -it euclid-omni bash
```

Local install:
```bash
conda create -n euclid-omni python=3.11 -y
conda activate euclid-omni
pip install .
```

Diagram caches are populated automatically on the first run of any benchmark; no extra extraction step is required.

Verify the installation by solving a single problem with proof generation:
```bash
python tests/test_single.py --help
python tests/test_single.py --show-proof
```
A line like `Solved in 8.90s` indicates a successful setup.

> **Note.** The proof generator uses Gurobi via PySCIPOpt. To solve more complex problems you may need a [Gurobi academic license](https://www.gurobi.com/academia/academic-program-and-licenses/); the free version caps variables and constraints at 2000.

## Reproducing the Paper

### Symbolic-solver evaluation (Table 1, Section 5.1)

We evaluate Euclidea on three benchmarks with a 600-second per-problem time limit. Sequential and SLURM-array runs are supported.

```bash
# Sequential, single machine
python tests/test_geometry3k.py        # Geometry3K  (601 problems)
python tests/test_jgex.py              # JGEX-AG-231 (231 problems)
python tests/test_imo.py               # IMO-AG-30   (30 problems)

# Parallel via SLURM (edit per cluster)
sbatch scripts/geometry3k_slurm.sh
sbatch scripts/jgex_slurm.sh
sbatch scripts/imo_slurm.sh
```

Each successful problem writes `proof.txt` and `diagram.jpg` into `results/<benchmark>/<idx>/`. Count solved problems with:
```bash
python summary.py results/JGEX-AG-231 --start 1 --end 231
python summary.py results/Geometry3K  --start 2401 --end 3001
python summary.py results/IMO-AG-30   --start 1 --end 30
```

### Synthetic data generation (Sections 3.2 and 5.4)

Euclid-Omni generates two problem families: **computational** (numeric calculation, optionally with auxiliary constructions) and **proving** (formal proof goals).

Sequential generation:
```bash
# Computational problems (with or without auxiliary constructions)
export PYTHONHASHSEED=0
export AUXILIARY_MODE=allow         # allow | forbid | must
export OUTPUT_DIR=dataset/calculation
export MAX_PROBLEM_ID=10
python scripts/generate_calculation.py

# Proving problems
export PYTHONHASHSEED=0
export OUTPUT_DIR=dataset/proving
export TIMEOUT_SECONDS=3600
export MAX_PROBLEM_ID=100
python scripts/generate_proving.py

# Auxiliary constructions for theorem proving (Task 3)
export PYTHONHASHSEED=0
export OUTPUT_DIR=dataset/auxiliary_construction
python scripts/generate_auxiliary_constructions.py
```

Parallel generation on a SLURM cluster:
```bash
sbatch scripts/generate_calculation_parallel.sh
sbatch scripts/generate_proving_parallel.sh
sbatch scripts/generate_auxiliary_constructions_parallel.sh
```

The SLURM scripts allocate 2 cores and 8 GB per task and shard work across array indices.

| Variable           | Meaning                                                                 | Default     |
|--------------------|-------------------------------------------------------------------------|-------------|
| `OUTPUT_DIR`       | Output directory for generated problems                                 | `dataset`   |
| `TIMEOUT_SECONDS`  | Per-task timeout (seconds)                                              | `3600`      |
| `MAX_PROBLEM_ID`   | Maximum number of problems per task (`0` = unlimited)                   | `0`         |
| `PYTHONHASHSEED`   | Seed for reproducibility (must be an integer)                           | `0`         |
| `AUXILIARY_MODE`   | `allow` / `forbid` / `must` for auxiliary-construction filtering        | `allow`     |

Each calculation problem is written as `data.json` (constructions, goal, proof, depth, auxiliary metadata) and `diagram.pdf`. Each proving problem is written as `data.json` and `diagram.jpg`, alongside `constructions_list.json`.

### Natural-language translation (Section 3.2, Appendix on informalization)

Synthetic symbolic problems are translated into natural language via manually verified templates plus paraphrasing by an LLM (Gemini 2.5 Flash in our experiments).

```bash
# Instantiate templates from generated symbolic problems
python scripts/informalize_template.py    --dataset_dir <generated-problems-dir>
python scripts/informalize_template_q.py  --dataset_dir <generated-problems-dir>
python scripts/informalize_template_eval.py --dataset_dir <generated-problems-dir>

# Paraphrase the drafts with an LLM
export GEMINI_API_KEY=...
python scripts/llm_informalize.py        --dataset_dir <generated-problems-dir>
python scripts/llm_refine.py             --dataset_dir <generated-problems-dir>
python scripts/llm_refine_q.py           --dataset_dir <generated-problems-dir>
```

### Training and neuro-symbolic evaluation (Sections 5.2 and 5.3)

We use [LLaMA-Factory](https://github.com/hiyouga/LLaMA-Factory) for supervised fine-tuning. Clone it next to this repo:
```bash
git clone https://github.com/hiyouga/LLaMA-Factory
pip install -e LLaMA-Factory
```

Build training datasets and launch SFT:
```bash
# Calculation VLM (Qwen2.5-VL-7B) — paper Section 5.2
python scripts/create_task1_dataset.py --dataset_dir <calculation-problems-dir> --out_json data/task1_train.json
llamafactory-cli train configs/train/task1.yaml

# Proving LLM (Qwen2.5-Math-7B) — paper Section 5.3
python scripts/create_dataset.py            # builds data/task3_train.json from auxiliary-construction problems
llamafactory-cli train configs/train/task3.yaml
```

Neuro-symbolic evaluation uses a vLLM server for our trained model and beam-search decoding for auxiliary constructions (branching factor 32, beam size 128, max depth 4, 90-minute budget per problem):
```bash
# Start the vLLM server (set ALLOWED_MEDIA_PATH if your data lives outside ./data)
sbatch scripts/start_vllm_server.sh

# Our model
sbatch scripts/eval_ours_jgex.sh
sbatch scripts/eval_ours_imo.sh

# Proprietary baselines
GEMINI_API_KEY=... sbatch scripts/eval_gemini_jgex.sh
GEMINI_API_KEY=... sbatch scripts/eval_gemini_imo.sh
OPENAI_API_KEY=... sbatch scripts/eval_openai_jgex.sh
OPENAI_API_KEY=... sbatch scripts/eval_openai_imo.sh
```

## Extension

To add a new inference rule, edit `pyeuclid/engine/inference_rule.py`. For example:
```python
@register('complex')
class AreaHeronFormula(InferenceRule):
    def __init__(self, a: Point, b: Point, c: Point):
        super().__init__()
        self.a = a
        self.b = b
        self.c = c

    def condition(self):
        return [NotCollinear(self.a, self.b, self.c), Different(self.a, self.b, self.c), Lt(self.a, self.b), Lt(self.b, self.c)]

    def conclusion(self):
        s = (Length(self.a, self.b)+Length(self.a, self.c)+Length(self.b, self.c))/2
        return [Area(self.a, self.b, self.c)**2-(s*(s-Length(self.a, self.b))*(s-Length(self.a, self.c))*(s-Length(self.b, self.c)))]
```
The `Lt` relation defines a partial order on point names to suppress equivalent permutations of the rule.

Euclidea also exposes an interactive interface that can be driven by a human or an LLM agent. A reasoning step is triggered by:
```python
engine.step(conditions, conclusions)
```
The engine verifies the conditions and conclusions and applies the appropriate theorems and algebraic equations to derive the conclusions.

## License

Euclid-Omni is released under the MIT License.
