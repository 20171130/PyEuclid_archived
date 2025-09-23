#!/bin/bash
#SBATCH --job-name=proving
#SBATCH --array=0-9999
#SBATCH --time=10:00:00
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --output=/dev/null
#SBATCH --error=/dev/null
#SBATCH --partition=learnfair,learnlab,devlab,scavenge

export OUTPUT_DIR=task2/proving_922
export TIMEOUT_SECONDS=36000
export MAX_PROBLEM_ID=0

python scripts/generate_proving.py