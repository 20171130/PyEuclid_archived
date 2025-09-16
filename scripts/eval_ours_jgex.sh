#!/bin/bash
#SBATCH -J eval_ours_jgex
#SBATCH -p learnfair,learnlab,devlab,scavenge
#SBATCH --cpus-per-task=35
#SBATCH --mem=10G
#SBATCH -t 1:30:00
#SBATCH --array=0-30
#SBATCH -o new_logs/%x_%A_%a.out

set -eo pipefail

# ============================
# Environment & Python setup
# ============================
module load cuda/12.1
source ~/.bashrc && conda activate euclidea

############################
# User-configurable knobs  #
############################

# Python entrypoint
PYMAIN="scripts/eval.py"

# Provider: vllm | gemini | openai (this script is for vLLM)
PROVIDER="vllm"

# vLLM model name (what the server loaded)
MODEL="saves/task3/qwen2.5-math-7b"

# Shared directory & hostfile written by the vLLM server job
SHARED_DIR=".vllm"
HOSTFILE="${SHARED_DIR}/vllm_server_host.txt"

# Data paths (edit as needed)
DATA_TXT="data/JGEX-AG-231.txt"
RESULTS_DIR="results/JGEX-AG-231"

# Search knobs
BRANCHING_FACTOR="${BRANCHING_FACTOR:-32}"
BEAM_SIZE="${BEAM_SIZE:-128}"
MAX_DEPTH="${MAX_DEPTH:-4}"

# Timeouts & workers
ENGINE_TIMEOUT="${ENGINE_TIMEOUT:-1200}"
PROOF_TIMEOUT="${PROOF_TIMEOUT:-1200}"
CPU_WORKERS="${CPU_WORKERS:-32}"

# Optional sampling (only passed if non-empty)
MAX_TOKENS="${MAX_TOKENS:-}"
TEMPERATURE="${TEMPERATURE:-}"
TOP_P="${TOP_P:-}"

############################
# Basic sanity checks
############################
if [[ ! -f "${PYMAIN}" ]]; then
  echo "ERROR: Cannot find ${PYMAIN} in $(pwd)"
  exit 1
fi

if [[ ! -f "${HOSTFILE}" ]]; then
  echo "[clients] ERROR: hostfile not found at ${HOSTFILE}"
  exit 2
fi

HP=$(<"${HOSTFILE}")
if [[ -z "${HP}" || "${HP}" != *:* ]]; then
  echo "[clients] ERROR: hostfile exists but invalid content: '${HP}'"
  exit 3
fi
SERVER_HOST="${HP%:*}"
SERVER_PORT="${HP#*:}"
VLLM_BASE_URL="http://${SERVER_HOST}:${SERVER_PORT}"

echo "[Slurm] JOB_ID=${SLURM_JOB_ID} TASK_ID=${SLURM_ARRAY_TASK_ID} TASK_COUNT=${SLURM_ARRAY_TASK_COUNT}"
echo "[Cfg]   PROVIDER=${PROVIDER}"
echo "[Cfg]   MODEL=${MODEL}"
echo "[Cfg]   DATA_TXT=${DATA_TXT} RESULTS_DIR=${RESULTS_DIR}"
echo "[Cfg]   BRANCHING=${BRANCHING_FACTOR} BEAM_SIZE=${BEAM_SIZE} MAX_DEPTH=${MAX_DEPTH}"
echo "[Cfg]   CPU_WORKERS=${CPU_WORKERS} ENGINE_TIMEOUT=${ENGINE_TIMEOUT} PROOF_TIMEOUT=${PROOF_TIMEOUT}"
echo "[Cfg]   MAX_TOKENS=${MAX_TOKENS} TEMPERATURE=${TEMPERATURE} TOP_P=${TOP_P}"
echo "[Cfg]   VLLM_BASE_URL=${VLLM_BASE_URL}"

############################
# Wait for server readiness
############################
READY=0
for i in {1..60}; do
  if curl -sf "${VLLM_BASE_URL}/v1/models" >/dev/null; then
    echo "[clients] vLLM server ready on ${VLLM_BASE_URL}"
    READY=1
    break
  fi
  sleep 2
done
if [[ "${READY}" -ne 1 ]]; then
  echo "[clients] ERROR: vLLM server not responding at ${VLLM_BASE_URL}"
  exit 4
fi

############################
# Build CLI
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

# Provider-specific args (vLLM)
if [[ "${PROVIDER}" == "vllm" ]]; then
  ARGS+=(--vllm-base-url "${VLLM_BASE_URL}" --vllm-model "${MODEL}")
elif [[ "${PROVIDER}" == "gemini" ]]; then
  : "${GEMINI_API_KEY:=${GEMINI_API_KEY:-}}"
  if [[ -z "${GEMINI_API_KEY}" ]]; then
    echo "ERROR: PROVIDER=gemini but GEMINI_API_KEY is empty."
    exit 5
  fi
  export GEMINI_API_KEY
  ARGS+=(--gemini-model "${GEMINI_MODEL:-gemini-2.5-pro}")
elif [[ "${PROVIDER}" == "openai" ]]; then
  : "${OPENAI_API_KEY:=${OPENAI_API_KEY:-}}"
  if [[ -z "${OPENAI_API_KEY}" ]]; then
    echo "ERROR: PROVIDER=openai but OPENAI_API_KEY is empty."
    exit 6
  fi
  export OPENAI_API_KEY
  ARGS+=(--openai-model "${OPENAI_MODEL:-gpt-4o-mini}")
else
  echo "ERROR: Unknown PROVIDER='${PROVIDER}'"
  exit 7
fi

# Optional sampling flags: only append if set
[[ -n "${MAX_TOKENS}" ]] && ARGS+=(--max-tokens "${MAX_TOKENS}")
[[ -n "${TEMPERATURE}" ]] && ARGS+=(--temperature "${TEMPERATURE}")
[[ -n "${TOP_P}" ]] && ARGS+=(--top-p "${TOP_P}")

############################
# Run
############################
echo "[Run] python -u ${PYMAIN} ${ARGS[*]}"
python -u "${PYMAIN}" "${ARGS[@]}"
