#!/bin/bash
#SBATCH --job-name=gen_calculation
#SBATCH --array=0-29
#SBATCH --time=2:00:00
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --output=logs/%x-%A_%a.out
#SBATCH --error=logs/%x-%A_%a.err

export PYTHONHASHSEED=0
export OUTPUT_DIR=calculation_problems
export TIMEOUT_SECONDS=3600
export MAX_PROBLEM_ID=0
# AUX_MODE options: "allow" (default), "forbid", "must"
export AUX_MODE=must

python scripts/generate_calculation.py