#!/bin/bash
#SBATCH -J eval_with_vllm_server
#SBATCH --cpus-per-task=35
#SBATCH --mem=8G
#SBATCH -t 2:00:00
#SBATCH --array=0-31
#SBATCH -o %A_%a.out

set -eo pipefail

MODEL="saves/qwen2_5-math-7b"
PORT="${PORT:-8000}"
SHARED_DIR=".vllm1"

module load cuda/12.1
source ~/.bashrc && conda activate euclidea

HOSTFILE="${SHARED_DIR}/vllm_server_host.txt"

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
export MODEL="${MODEL}"

export TOTAL_BEAMS="${TOTAL_BEAMS:-32}"
export N_PER_CALL="${N_PER_CALL:-32}"
export CPU_WORKERS="${CPU_WORKERS:-32}"
export ENGINE_TIMEOUT="${ENGINE_TIMEOUT:-1200}"
export PROOF_TIMEOUT="${PROOF_TIMEOUT:-1200}"

for i in {1..60}; do
  if curl -sf "${VLLM_BASE_URL}/v1/models" >/dev/null; then
    echo "vLLM server ready on ${VLLM_BASE_URL}"
    break
  fi
  sleep 2
done

python -u eval.py \
  --base-url "http://${SERVER_HOST}:${SERVER_PORT}" \
  --model "${MODEL}" \
  --total-beams "${TOTAL_BEAMS}" \
  --n-per-call "${N_PER_CALL}" \
  --cpu-workers "${CPU_WORKERS}" \
  --engine-timeout "${ENGINE_TIMEOUT}" \
  --proof-timeout "${PROOF_TIMEOUT}" \
