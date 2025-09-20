#!/bin/bash
#SBATCH -J eval_gemini_imo
#SBATCH -p learnfair,learnlab,devlab,scavenge
#SBATCH --cpus-per-task=35
#SBATCH --mem=10G
#SBATCH -t 1:30:00
#SBATCH --array=0-15
#SBATCH -o new_logs/%x_%A_%a.out

set -eo pipefail

source ~/.bashrc && conda activate euclidea

############################
# User-configurable knobs  #
############################

# Python entrypoint (your file name here)
PYMAIN="scripts/eval.py"

# Provider: gemini | openai
PROVIDER="gemini"

# Models
GEMINI_MODEL="${GEMINI_MODEL:-gemini-2.5-flash}"

# API keys (must be set in env or here)
: "${GEMINI_API_KEY:=${GEMINI_API_KEY:-}}"

# Data paths (NEW)
DATA_TXT="data/IMO-AG-30.txt"
RESULTS_DIR="results/IMO-AG-30"

# Beam search knobs
BRANCHING_FACTOR="${BRANCHING_FACTOR:-32}"
BEAM_SIZE="${BEAM_SIZE:-128}"
MAX_DEPTH="${MAX_DEPTH:-4}"

# Timeouts & CPU workers
ENGINE_TIMEOUT="${ENGINE_TIMEOUT:-1200}"
PROOF_TIMEOUT="${PROOF_TIMEOUT:-1200}"
CPU_WORKERS="${CPU_WORKERS:-32}"
PROBLEM_TIMEOUT="${PROBLEM_TIMEOUT:-5400}"

# Basic sanity checks
if [[ ! -f "${PYMAIN}" ]]; then
  echo "ERROR: Cannot find ${PYMAIN} in $(pwd)"
  exit 1
fi

if [[ "${PROVIDER}" == "gemini" && -z "${GEMINI_API_KEY}" ]]; then
  echo "ERROR: PROVIDER=gemini but GEMINI_API_KEY is empty."
  exit 2
fi

echo "[Slurm] JOB_ID=${SLURM_JOB_ID} TASK_ID=${SLURM_ARRAY_TASK_ID} TASK_COUNT=${SLURM_ARRAY_TASK_COUNT}"
echo "[Cfg]   PROVIDER=${PROVIDER} GEMINI_MODEL=${GEMINI_MODEL} OPENAI_MODEL=${OPENAI_MODEL}"
echo "[Cfg]   DATA_TXT=${DATA_TXT} RESULTS_DIR=${RESULTS_DIR}"
echo "[Cfg]   BRANCHING=${BRANCHING_FACTOR} BEAM_SIZE=${BEAM_SIZE} MAX_DEPTH=${MAX_DEPTH}"
echo "[Cfg]   CPU_WORKERS=${CPU_WORKERS} ENGINE_TIMEOUT=${ENGINE_TIMEOUT} PROOF_TIMEOUT=${PROOF_TIMEOUT} PROBLEM_TIMEOUT=${PROBLEM_TIMEOUT}"
echo "[Cfg]   MAX_TOKENS=${MAX_TOKENS} TEMPERATURE=${TEMPERATURE} TOP_P=${TOP_P}"

############################
# Build CLI                #
############################
ARGS=(
  --provider "${PROVIDER}"
  --data-txt "${DATA_TXT}"
  --results-dir "${RESULTS_DIR}"
  --branching-factor "${BRANCHING_FACTOR}"
  --beam-size "${BEAM_SIZE}"
  --max-depth "${MAX_DEPTH}"
  --cpu-workers "${CPU_WORKERS}"
  --engine-timeout "${ENGINE_TIMEOUT}"
  --proof-timeout "${PROOF_TIMEOUT}"
)

if [[ "${PROVIDER}" == "gemini" ]]; then
  export GEMINI_API_KEY
  ARGS+=(--gemini-model "${GEMINI_MODEL}")
elif [[ "${PROVIDER}" == "openai" ]]; then
  export OPENAI_API_KEY
  ARGS+=(--openai-model "${OPENAI_MODEL}")
else
  echo "ERROR: Unknown PROVIDER='${PROVIDER}'"
  exit 4
fi

############################
# Run                      #
############################
echo "[Run] python -u ${PYMAIN} ${ARGS[*]}"
python -u "${PYMAIN}" "${ARGS[@]}"
