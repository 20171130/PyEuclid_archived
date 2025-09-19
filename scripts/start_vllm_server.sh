#!/bin/bash
#SBATCH -J vllm-server
#SBATCH -p learnfair,learnlab,scavenge
#SBATCH --gres=gpu:ampere:1
#SBATCH --cpus-per-task=10
#SBATCH --mem=60G
#SBATCH -t 12:00:00
#SBATCH -o %A_%a.out

set -eo pipefail

# MODEL="saves/task2/918/qwen2.5-vl-7b"
MODEL="Qwen/Qwen2.5-VL-7B-Instruct"
PORT="${PORT:-8000}"
SHARED_DIR=".vllm"
HOST="0.0.0.0"

module load cuda/12.1
source ~/.bashrc && conda activate euclidea

mkdir -p "${SHARED_DIR}"
HOSTFILE="${SHARED_DIR}/vllm_server_host.txt"

echo "${HOSTNAME}:${PORT}" > "${HOSTFILE}"
echo "[`date`] Launching vLLM on ${HOSTNAME}:${PORT}"

NGPUS=$(nvidia-smi --query-gpu=index --format=csv,noheader 2>/dev/null | wc -l)

vllm serve "${MODEL}" \
  --host "${HOST}" \
  --port "${PORT}" \
  --dtype auto \
  --tensor-parallel-size "${NGPUS}" \
  --allowed-local-media-path /private/home/zhaoyuli/PyEuclid_archived/data/task2/eval/images
