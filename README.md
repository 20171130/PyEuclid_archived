# PyEuclid: A Versatile Formal Plane Geometry System in Python

## Computational Recourses
We conduct our experiments on a server running Ubuntu 22.04.5 LTS with an AMD Ryzen Threadripper 2990WX processor, utilizing 30 CPU cores in parallel (2 cores per process, each allocated 4 GB of memory). On this setup, experiments on the JGEX-AG-231 dataset take approximately 2 hours to complete, while the Geometry3K dataset takes around 1 hour.

Additionally, we run sequential experiments on an Apple MacBook Pro with an M3 chip, using 2 CPU cores and 4 GB of memory. On this setup, processing the Geometry3K dataset takes approximately 7~8 hours.

## Folder Structure
```
.
├── cache/                                # Cached diagrams sampled from JGEX-AG-231
├── data/                                 # Benchmark datasets (JGEX-AG-231, Geometry3K)
├── pyeuclid/
│   ├── engine/                           # Core reasoning components: inference rules, deductive database, algebraic system, proof generator
│   └── formalization/                    # Problem formalization: relations, construction rules, state management, diagram handling
├── Dockerfile                            # Docker configuration for containerized setup
├── requirements.txt                      # List of required Python packages
├── setup.py                              # Setup script to build and install PyEuclid
└── test.py                               # Run experiments on test datasets
```

## Installation
You can get started with PyEuclid using Docker or a local installation.

You can either build the Docker image locally or pull it from Docker Hub:
```bash
# Build the Docker image locally
docker build -t pyeuclid .
# Alternatively, pull the image from Docker Hub
docker pull dahubao/pyeuclid
# After obtaining the image, run
docker run -it pyeuclid bash
```

To install PyEuclid locally *without* Docker, run:
```bash
conda create -n pyeuclid python=3.11 -y
conda activate pyeuclid
cd PyEuclid
pip install .
tar -xvzf cache.tar.gz
```

After installation, verify that everything is working by running:
```bash
python tests/test_single.py --help
python tests/test_single.py --show-proof
```

If you see output like `Solved in 8.90s`, the setup is successful.



Note:
PyEuclid uses Gurobi as a component of its proof generator.
To solve more complex problems, you may need a [Gurobi academic license](https://www.gurobi.com/academia/academic-program-and-licenses/), as the free version has a limit of 2000 variables and constraints, which may not be sufficient for certain cases.


## Generating Problems

### Computational and Proving Problems
PyEuclid can generate two types of geometry problems: **computational problems** (requiring numeric calculations) and **proving problems** (requiring formal proofs).

#### Problem Types

**Computational Problems** are numeric calculation tasks that require students to compute geometric quantities (lengths, angles, ratios). These can be generated:
- **Without auxiliary constructions**: Problems solvable using must the given geometric constructions
- **With auxiliary constructions**: More challenging problems that require additional helper constructions to reach the solution

**Proving Problems** require formal geometric proof generation.

#### Sequential Generation
For small-scale problem generation on a single machine:

```bash
# Generate computational problems (accept both with and without auxiliary constructions)
python tests/test_generate.py

# Generate ONLY computational problems WITHOUT auxiliary constructions
export PYTHONHASHSEED=0
export AUXILIARY_MODE=forbid
export MAX_PROBLEM_ID=10
python tests/test_generate.py

# Generate ONLY computational problems WITH auxiliary constructions
export PYTHONHASHSEED=0
export AUXILIARY_MODE=must
export MAX_PROBLEM_ID=10
python tests/test_generate.py

# OR generate proving problems
export PYTHONHASHSEED=0
export OUTPUT_DIR=dataset/proving
export TIMEOUT_SECONDS=3600
export MAX_PROBLEM_ID=100
python scripts/generate_proving.py
```

#### Parallel Generation with SLURM
For large-scale problem generation on a compute cluster:

```bash
# Generate computational problems in parallel (with auxiliary construction support)
sbatch scripts/generate_calculation_parallel.sh

# Generate proving problems in parallel
sbatch scripts/generate_proving_parallel.sh

# Generate auxiliary constructions in parallel
sbatch scripts/generate_auxiliary_constructions_parallel.sh
```

The SLURM scripts automatically configure:
- Array job distribution across cluster nodes
- Per-task CPU and memory allocation (2 cores, 8GB per task)
- Timeout and problem limits via environment variables
- Output directory structure with rank-based organization

**Generated Problem Structure:**
Each computational problem includes:
- `data.json`: Problem metadata (necessary constructions, auxiliary constructions, goal, proof, depth, etc.)
- `diagram.pdf`: Visual diagram of the geometric configuration
- `necessary_constructions`: Minimal constructions required for solving
- `auxiliary_constructions`: Additional constructions needed if solvable must with their help
- `has_auxiliary_constructions`: Boolean flag indicating if auxiliaries were required
- `num_auxiliary_constructions`: Count of auxiliary constructions used

Each proving problem includes:
- `data.json`: Problem metadata (constructions, goals, proofs, coordinates, depth)
- `diagram.jpg`: Visual diagram of the geometric configuration
- `constructions_list.json`: Complete construction sequence

### Environment Variables for Problem Generation
- `OUTPUT_DIR`: Output directory for generated problems (default: `dataset`)
- `TIMEOUT_SECONDS`: Timeout per SLURM task in seconds (default: `3600`)
- `MAX_PROBLEM_ID`: Maximum number of problems to generate per task (0 = unlimited)
- `PYTHONHASHSEED`: Must be set to an integer for reproducibility (e.g., `0`)
- `AUXILIARY_MODE`: Control auxiliary construction filtering for computational problems (default: `allow`)
  - `allow`: Accept problems with or without auxiliary constructions
  - `forbid`: Only accept problems without auxiliary constructions
  - `must`: Only accept problems with auxiliary constructions

## Evaluation
We provide both sequential and parallel methods to run experiments on the JGEX-AG-231 and Geometry3K datasets:
```bash
python tests/test.py                            # Run sequentially on a single machine
sbatch scripts/slurm.sh                           # Run in parallel on a compute cluster via SLURM
```

## Extension
If you would like to improve the reasoning ability of PyEuclid, one straightforward way is to add more complex inference rule at `pyeuclid/engine/inference_rule.py`. Here is an example:
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
You need to specify the condition and conclusion of the inference rule. The Lt relation defines a partial order on the names of the points to reduce equivalent permutations of the inference rule.

We also provide an interactive interface that allows PyEuclid to collaborate with a human user or a Large-Language-Model (LLM) agent.
You can explicitly trigger a reasoning step by calling:
```python
engine.step(conditions, conclusions)
```
PyEuclid will verify both the conditions and the desired conclusions, and automatically apply the appropriate theorems or algebraic equations to derive the conclusions from the given conditions.

## License
PyEuclid is licensed under the MIT License.