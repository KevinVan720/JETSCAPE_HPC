#!/bin/sh
#SBATCH -q 
#SBATCH --constraint=haswell

#SBATCH -N 1
#SBATCH -c 1
#SBATCH -n 32
#SBATCH --license cscratch1

#SBATCH --job-name=MA
#SBATCH --time 12:00:00

srun --multi-prog run.conf