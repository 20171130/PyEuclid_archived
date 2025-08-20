#!/bin/bash
#SBATCH -J vllm-server
#SBATCH --gres=gpu:ampere:4
#SBATCH --cpus-per-task=12
#SBATCH --mem=128G
#SBATCH -t 12:00:00
#SBATCH -N 1

set -eo pipefail

MODEL="saves/qwen2_5-math-7b/full/sft"
PORT="${PORT:-8000}"
SHARED_DIR=".vllm"
HOST="0.0.0.0"

module load cuda/12.1
source ~/.bashrc && conda activate pyeuclid

mkdir -p "${SHARED_DIR}"
HOSTFILE="${SHARED_DIR}/vllm_server_host.txt"
JOBFILE="${SHARED_DIR}/vllm_server_jobid.txt"

echo "${SLURM_JOB_ID}" > "${JOBFILE}"
echo "${HOSTNAME}:${PORT}" > "${HOSTFILE}"

echo "[`date`] Launching vLLM on ${HOSTNAME}:${PORT} (job ${SLURM_JOB_ID})"
echo "[info] Hostfile: ${HOSTFILE}  Jobfile: ${JOBFILE}"

vllm serve "${MODEL}" \
  --host "${HOST}" \
  --port "${PORT}" \
  --dtype auto \
  --tensor-parallel-size "${SLURM_GPUS_PER_TASK:-${SLURM_GPUS_ON_NODE:-4}}"
