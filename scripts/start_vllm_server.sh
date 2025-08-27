#!/bin/bash
#SBATCH -J vllm-server
#SBATCH -p learnfair,learnlab,scavenge
#SBATCH --gres=gpu:ampere:4
#SBATCH --cpus-per-task=8
#SBATCH --mem=60G
#SBATCH -t 12:00:00
#SBATCH -o %A_%a.out

set -eo pipefail

MODEL="saves/qwen2_5-math-7b"
PORT="${PORT:-8000}"
SHARED_DIR=".vllm"
HOST="0.0.0.0"

module load cuda/12.1
source ~/.bashrc && conda activate euclidea

mkdir -p "${SHARED_DIR}"
HOSTFILE="${SHARED_DIR}/vllm_server_host.txt"

echo "${HOSTNAME}:${PORT}" > "${HOSTFILE}"
echo "[`date`] Launching vLLM on ${HOSTNAME}:${PORT}"

vllm serve "${MODEL}" \
  --host "${HOST}" \
  --port "${PORT}" \
  --dtype auto \
  --tensor-parallel-size "${SLURM_GPUS_PER_TASK:-${SLURM_GPUS_ON_NODE:-4}}"
