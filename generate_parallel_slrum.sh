#!/bin/bash
#SBATCH --job-name=geom_sample                  # Job name
#SBATCH --output=logs/%A_%a.out                 # Standard output log (%A = job ID, %a = array task ID)
#SBATCH --error=logs/%A_%a.err                  # Standard error log
#SBATCH --array=0-999                            # Launch 1000 parallel tasks (array indices 0 through 999)
#SBATCH --time=24:00:00                         # Max time per task
#SBATCH --cpus-per-task=2                       # Number of CPU cores per task
#SBATCH --mem=2G                                # Memory per task

# Set environment variables for use in generate_parallel.py
export OUTPUT_DIR=synthetic_dataset
export TIMEOUT_SECONDS=86400                   # Per-task timeout in seconds
export MAX_PROBLEM_ID=0                        # Number of problems to generate per task

# Run Python script
python generate_parallel.py

SAMPLE_COUNT=$(find "$OUTPUT_DIR" -type f -path "$OUTPUT_DIR/rank_*/problem_*/sample_*/data.json" | wc -l)
echo "Generated $SAMPLE_COUNT data.json files in task ID $SLURM_ARRAY_TASK_ID"
