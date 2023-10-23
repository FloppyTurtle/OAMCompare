@echo off

set MKL_NUM_THREADS=12
set NUMBA_NUM_THREADS=12
set OMP_NUM_THREADS=12

echo "MKL Thread number   :" %MKL_NUM_THREADS%
echo "Numba Thread number :" %NUMBA_NUM_THREADS%
echo "OMP Thread number   :" %OMP_NUM_THREADS%

python OAMCompare\Code\Order_Test.py 2
python OAMCompare\Code\FBPIC_Image.py Order_2
