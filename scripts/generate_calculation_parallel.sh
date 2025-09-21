#!/bin/bash
#SBATCH --job-name=gen_calculation
#SBATCH --array=0-9999
#SBATCH --time=2:00:00
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --output=/dev/null
#SBATCH --error=/dev/null
#SBATCH --partition=learnfair,learnlab,devlab,scavenge

export OUTPUT_DIR=task1/calculation_922
export TIMEOUT_SECONDS=7200
export MAX_PROBLEM_ID=0

PYTHONHASHSEED=0 python tests/test_generate.py 