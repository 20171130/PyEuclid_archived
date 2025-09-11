#!/bin/bash

#SBATCH --job-name=JGEX_AG_231
#SBATCH -n 1
#SBATCH --time=2:00:00
#SBATCH --cpus-per-task=2
#SBATCH --mem-per-cpu=16G

export PYTHONBREAKPOINT=0

mpirun python3 tests/test_generate.py
