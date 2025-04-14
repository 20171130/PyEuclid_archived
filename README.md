# Installation

```bash
docker build -t pyeuclid . # build the image locally
# alternatively, pull from dockerhub
docker run pyeuclid # run on an example problem
```

You may need a [gurobi license](https://www.gurobi.com/academia/academic-program-and-licenses/) to generate proofs for some problems.
# Test
```bash
python test.py # on a single node
sbatch slurm.sh # distributed
```
