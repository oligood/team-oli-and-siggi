#!/bin/bash
# JURECA HPC Sidequest Job - Statistics Iceland Table Indexing & GPU Acceleration
# Submit from the repo folder on JURECA:
#   sbatch scripts/jureca_sidequest.sbatch
#
#SBATCH --job-name=hagstofa_hpc
#SBATCH --account=training2654
#SBATCH --partition=dc-gpu-devel
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --gres=gpu:1
#SBATCH --time=00:15:00
#SBATCH --output=slurm-%x-%j.out

echo "=========================================="
echo " Starting JURECA HPC Job on $(hostname)"
echo " Date: $(date)"
echo "=========================================="

module load Stages/2026 GCCcore/.14.3.0 PyTorch/2.9.1

echo ""
echo "--- GPU Hardware Verification ---"
nvidia-smi

echo ""
echo "--- Running HPC Table Indexing & Similarity Benchmark ---"
srun python scripts/hpc_embed_tables.py

echo ""
echo "=========================================="
echo " Finished JURECA HPC Job at $(date)"
echo "=========================================="
