#!/bin/bash
#SBATCH --job-name=gen_calculation
#SBATCH --array=0-4999
#SBATCH --time=00:10:00
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --output=/dev/null
#SBATCH --error=/dev/null
#SBATCH --partition=learnfair,learnlab,devlab,scavenge

export OUTPUT_DIR=task1/calculation_922_new
export TIMEOUT_SECONDS=600
export MAX_PROBLEM_ID=0

PYTHONHASHSEED=0 python tests/test_generate.py 