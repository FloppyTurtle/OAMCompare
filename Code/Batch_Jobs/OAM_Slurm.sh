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

module load Python/3.11.3-GCCcore-12.3.0
module load CUDA/12.2.2
module load MPICH/3.4.2-GCC-10.3.0


: << 'END'
END
max=2

for (( i=32; i >= $max; i=i/2 ))
do
    echo "$i"
    echo Starting FBPIC run...
    PATH=Gaussian_NCR_test_${i}
    python_environments/envs/OAM/bin/python3.11 OAMCompare/Code/NCR_test.py 4.0 6.7 20 15 $PATH ${i}
    cp "OAMCompare/Code/Batch_Jobs/OAM_Slurm.sh" $PATH
    echo Finished the simulation
    echo Starting processing 
    python_environments/envs/OAM/bin/python3.11 -X importtime OAMCompare/Code/FBPIC_Image_Viking.py $PATH
    echo after python
done




echo
echo Job completed at `date`
