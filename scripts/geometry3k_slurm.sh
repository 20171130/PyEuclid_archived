#!/bin/bash

#SBATCH --job-name=Geometry3k
#SBATCH -n 100
#SBATCH --time=2:00:00
#SBATCH --cpus-per-task=2
#SBATCH --mem-per-cpu=4G
#SBATCH --partition=learnfair,learnlab,devlab,scavenge

export PYTHONBREAKPOINT=0

mpirun python3 tests/test_geometry3k.py
