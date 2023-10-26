@echo off

set MKL_NUM_THREADS=12
set NUMBA_NUM_THREADS=12
set OMP_NUM_THREADS=12

echo "MKL Thread number   :" %MKL_NUM_THREADS%
echo "Numba Thread number :" %NUMBA_NUM_THREADS%
echo "OMP Thread number   :" %OMP_NUM_THREADS%

for /l %%x in (50,5,100) do (
    echo %%x
    rmdir /S /Q diags
    python OAMCompare\Code\Laguerre_waist_var.py %%x ^
    && python OAMCompare\Code\FBPIC_Image.py %%x_waist_laguerre
)









