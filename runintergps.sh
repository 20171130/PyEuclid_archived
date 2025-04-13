#!/bin/bash
#SBATCH --job-name=imosolver
#SBATCH --partition=cpunodes
#SBATCH --time=12:00:00           # or adjust to your needs (240 mins = 4 hours)
#SBATCH -c 64
#SBATCH --mem=200G
#SBATCH --output=slurm_output/slurm-%j.out
#SBATCH --error=slurm_output/slurm-%j.err

# Load required modules and activate Conda
source /u/sjl/miniconda3/etc/profile.d/conda.sh
conda init
conda activate pyeuclid
# Run your command
export PYTHONBREAKPOINT=0
python test_intergps_dataset.py
