#!/bin/bash
#SBATCH --job-name=auxiliary_constructions
#SBATCH --array=0-19999
#SBATCH --time=72:00:00
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G
#SBATCH --output=/dev/null
#SBATCH --error=/dev/null
#SBATCH --partition=learnfair,learnlab,devlab,scavenge

export OUTPUT_DIR=dataset/auxiliary_construction
export TIMEOUT_SECONDS=259200
export MAX_PROBLEM_ID=0

python scripts/generate_auxiliary_constructions.py