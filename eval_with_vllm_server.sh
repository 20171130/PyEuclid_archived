#!/bin/bash
#SBATCH -J vllm-clients
#SBATCH --cpus-per-task=35
#SBATCH --mem=8G
#SBATCH -t 2:00:00
#SBATCH --array=0-31

set -eo pipefail

MODEL="saves/qwen2_5-math-7b/full/sft"
PORT="${PORT:-8000}"
SHARED_DIR=".vllm"

module load cuda/12.1
source ~/.bashrc && conda activate pyeuclid

HOSTFILE="${SHARED_DIR}/vllm_server_host.txt"
JOBFILE="${SHARED_DIR}/vllm_server_jobid.txt"

if [[ -f "${HOSTFILE}" ]]; then
  HP=$(<"${HOSTFILE}")
  if [[ -z "${HP}" || "${HP}" != *:* ]]; then
    echo "[clients] ERROR: hostfile exists but invalid content: '${HP}'"
    exit 1
  fi
  SERVER_HOST="${HP%:*}"
  SERVER_PORT="${HP#*:}"
  echo "[clients] Using server from hostfile: ${SERVER_HOST}:${SERVER_PORT}"
else
  echo "[clients] ERROR: hostfile not found at ${HOSTFILE}"
  exit 1
fi

export VLLM_BASE_URL="http://${SERVER_HOST}:${SERVER_PORT}"
export VLLM_MODEL="${MODEL}"

export TOTAL_BEAMS="${TOTAL_BEAMS:-32}"
export N_PER_CALL="${N_PER_CALL:-32}"
export CPU_WORKERS="${CPU_WORKERS:-32}"
export NUM_ENGINE_TIMEOUT="${NUM_ENGINE_TIMEOUT:-1200}"
export NUM_PROOF_TIMEOUT="${NUM_PROOF_TIMEOUT:-1200}"

for i in {1..60}; do
  if curl -sf "${VLLM_BASE_URL}/v1/models" >/dev/null; then
    echo "vLLM server ready on ${VLLM_BASE_URL}"
    break
  fi
  sleep 2
done

python eval.py
