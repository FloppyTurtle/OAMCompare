@echo off
echo "This is a test"

set MKL_NUM_THREADS=12
set NUMBA_NUM_THREADS=12
set OMP_NUM_THREADS=12

echo "MKL Thread number   :" %MKL_NUM_THREADS%
echo "Numba Thread number :" %NUMBA_NUM_THREADS%
echo "OMP Thread number   :" %OMP_NUM_THREADS%



