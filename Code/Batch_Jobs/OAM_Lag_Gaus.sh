#!/bin/sh
#SBATCH --job-name=FBPIC_SIMULATION_ADH542              # Job name
#SBATCH --output=OAM_Run_%j.log           # Standard out and error log
#SBATCH --mail-type=END,FAIL                  # Specify when to mail (NONE, BEGIN, END, FAIL, ALL)
#SBATCH --mail-user=adh542@york.ac.uk         # NB change uid to your username if wanting to send mail

#need ONE of the following two lines:
#SBATCH --partition=gpu                  # Partition
#SBATCH --gres=gpu:2                     # GPU Num
#SBATCH --account=pet-lwa-2019           

#customise these according to job size and time required:
#SBATCH --ntasks=1                         # Run 4 MPI tasks...
#SBATCH --cpus-per-task=1                  # ...with each task using 1 core
#SBATCH --time=24:00:00                    # Time limit hrs:min:sec
#SBATCH --mem=16gb

echo My working directory is `pwd`
echo Running job on host:
echo -e '\t'`hostname` at `date`
echo

export MPLBACKEND=TKAgg
export OMP_NUM_THREADS=8
export MKL_NUM_THREADS=8
export NUMBA_NUM_THREADS=8
export FBPIC_ENABLE_GPUDIRECT=1

module load Miniconda3
source activate OAM

module load CUDA/12.2.2
module load OpenMPI/4.1.5-GCC-12.3.0
module load Python/3.11.3-GCCcore-12.3.0

: << 'END'
END
max=40

for (( i=15; i < $max; i=i+5 ))
do
    echo "$i"
    PATH=Laguerre_Gaussian_dur_$i
    echo Starting FBPIC run...
    python_environments/envs/OAM/bin/python3.11 OAMCompare/Code/Laguerre_Gaus_4_variable.py 4 7.5 $i 15 $PATH
    echo Finished the simulation
    echo Starting processing 
    python_environments/envs/OAM/bin/python3.11 -X importtime OAMCompare/Code/FBPIC_Image_Viking.py $PATH
done




echo
echo Job completed at `date`
