#!/bin/bash

#SBATCH --job-name=JGEX_AG_231
#SBATCH -n 30
#SBATCH --time=2:00:00
#SBATCH --cpus-per-task=2
#SBATCH --mem-per-cpu=4G
#SBTACH --qos=formal_math_reasoning_high

export PYTHONBREAKPOINT=0

mpirun python3 test.py
