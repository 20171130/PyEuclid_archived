#!/bin/bash
#SBATCH --job-name=gen_calculation
#SBATCH --array=0-4999
#SBATCH --time=1:00:00
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --output=923_logs/%x-%A_%a.out    # logs/gen_calc-<jobid>_<task>.out
#SBATCH --error=923_logs/%x-%A_%a.err
#SBATCH --partition=learnfair,learnlab,devlab,scavenge

export OUTPUT_DIR=task1/calculation_923_new2
export TIMEOUT_SECONDS=3600
export MAX_PROBLEM_ID=0

PYTHONHASHSEED=0 python tests/test_generate.py 