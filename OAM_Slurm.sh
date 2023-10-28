#!/bin/sh
#SBATCH --job-name=MPI_test_adh542              # Job name
#SBATCH --output=MPI_test_%j.log           # Standard out and error log
#SBATCH --mail-type=NONE                   # Specify when to mail (NONE, BEGIN, END, FAIL, ALL)
#SBATCH --mail-user=adh542@york.ac.uk         # NB change uid to your username if wanting to send mail

#need ONE of the following two lines:
#SBATCH --partition=teach                  # priority queue for class work
#SBATCH --account=pet-lwa-2019           # specify your project account if NOT doing class work

#customise these according to job size and time required:
#SBATCH --ntasks=4                         # Run 4 MPI tasks...
#SBATCH --cpus-per-task=1                  # ...with each task using 1 core
#SBATCH --time=00:00:30                    # Time limit hrs:min:sec

#actual executable info now:
EXEC="./beads.exe"

#tell user what is going on:
echo My working directory is `pwd`
echo Running job on host:
echo -e '\t'`hostname` at `date`
echo -e '\t'using $SLURM_NTASKS MPI tasks
echo

mpiexec -n ${SLURM_NTASKS} $EXEC

echo
echo Job completed at `date`
