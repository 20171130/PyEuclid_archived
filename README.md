# [#259] PyEuclid: A Versatile Formal Plane Geometry System in Python

## Claimed Badges
Available badge, functional badge, and reusable badge

## DOI
10.5281/zenodo.15213812

## Computational Recourses
We conduct our experiments on a server running Ubuntu 22.04.5 LTS with an AMD Ryzen Threadripper 2990WX processor, utilizing 30 CPU cores in parallel (2 cores per process, each allocated 4 GB of memory). On this setup, experiments on the JGEX-AG-231 dataset take approximately 2 hours to complete, while the Geometry3K dataset takes around 1 hour.

Additionally, we run sequential experiments on an Apple MacBook Pro with an M3 chip, using 2 CPU cores and 4 GB of memory. On this setup, processing the Geometry3K dataset takes approximately 5 hours.

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

You can either build the Docker image locally or run it directly from Docker Hub:
```bash
# Build the Docker image locally
docker build -t pyeuclid .
# Alternatively, pull the image from Docker Hub
docker run pyeuclid
```

To install PyEuclid locally without Docker, run:
```bash
bash scripts/install.sh
```

After installation, verify that everything is working by running:
```bash
python test_single.py
```

If you see output like `Solved in 8.90s.`, the setup is successful.

Note:
PyEuclid uses Gurobi as a component of its proof generator.
To solve more complex problems, you may need a [Gurobi academic license](https://www.gurobi.com/academia/academic-program-and-licenses/), as the free version has a limit of 2000 variables and constraints, which may not be sufficient for certain cases.


## Evaluation
We provide both sequential and parallel methods to run experiments on the JGEX-AG-231 and Geometry3K datasets:
```bash
python test.py                            # Run sequentially on a single machine
sbatch slurm.sh                           # Run in parallel on a compute cluster via SLURM
```

To run experiments on a specific dataset, use the `--exp` argument:
```bash
# Run only on the JGEX-AG-231 dataset
python test.py --exp jgex-ag-231
# Run only on the Geometry3K dataset
python test.py --exp geoemtry3k
# Run both datasets (default setup)
python test.py --exp jgex-ag-231 geoemtry3k
```

If you would like to display the generated proof after solving a problem, use the `--show_proof` flag:

```bash
python test.py --show_proof
```
After running the experiments, you should see summary outputs indicating the number of solved problems:
For the JGEX-AG-231 dataset, you should see something like:
```
Solved 203 problems out of 231.
```
For the Geometry3K dataset, the expected output is at least:
```
Solved 567 problems out of 599.
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
You may need to specify the `condition` and `conclusion` of the inference rule, the `Lt` relation is a partial order of the used points to specify to reduce the permutation of the inference rules.

We also provide an interactive interface that allows PyEuclid to collaborate with human users—or even language models (LLMs).
You can explicitly trigger a reasoning step by calling:
```python
engine.step(conditions, conclusions)
```
PyEuclid will verify both the conditions and the desired conclusions, and automatically apply the appropriate theorems or algebraic equations to derive the conclusions from the given conditions.

## License
PyEuclid is licensed under the MIT License.