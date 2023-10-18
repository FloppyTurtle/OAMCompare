@echo off

rmdir /S /Q diags ^
python OAMCompare\Code\Co nvergence-test.py 20 50 && python OAMCompare\Code\FBPIC_Image.py Conv_20_50 ^
&& rmdir /S /Q diags ^
&& python OAMCompare\Code\Convergence-test.py 30 50 && python OAMCompare\Code\FBPIC_Image.py Conv_30_50 ^
&& rmdir /S /Q diags ^
&& python OAMCompare\Code\Convergence-test.py 40 50 && python OAMCompare\Code\FBPIC_Image.py Conv_40_50 ^
&& rmdir /S /Q diags ^
&& python OAMCompare\Code\Convergence-test.py 50 50 && python OAMCompare\Code\FBPIC_Image.py Conv_50_50 ^
&& rmdir /S /Q diags ^
&& python OAMCompare\Code\Convergence-test.py 100 50 && python OAMCompare\Code\FBPIC_Image.py Conv_100_50 ^
&& rmdir /S /Q diags ^
&& python OAMCompare\Code\Convergence-test.py 20 100 && python OAMCompare\Code\FBPIC_Image.py Conv_20_100 ^
&& rmdir /S /Q diags ^
&& python OAMCompare\Code\Convergence-test.py 20 200 && python OAMCompare\Code\FBPIC_Image.py Conv_20_200 ^
&& rmdir /S /Q diags ^
&& python OAMCompare\Code\Convergence-test.py 20 400 && python OAMCompare\Code\FBPIC_Image.py Conv_20_400 ^
&& rmdir /S /Q diags ^
&& python OAMCompare\Code\Convergence-test.py 20 800 && python OAMCompare\Code\FBPIC_Image.py Conv_20_800 ^
&& rmdir /S /Q diags ^
python OAMCompare\Code\Convergence-test.py 10 50 && python OAMCompare\Code\FBPIC_Image.py Conv_10_50 ^
&& rmdir /S /Q diags ^
&& python OAMCompare\Code\Convergence-test.py 20 200 && python OAMCompare\Code\FBPIC_Image.py Conv_20_200 ^
&& rmdir /S /Q diags ^
&& python OAMCompare\Code\Convergence-test.py 20 200 && python OAMCompare\Code\FBPIC_Image.py Conv_20_200 ^
&& rmdir /S /Q diags ^
&& python OAMCompare\Code\Convergence-test.py 30 300 && python OAMCompare\Code\FBPIC_Image.py Conv_30_300 ^
&& rmdir /S /Q diags ^
&& python OAMCompare\Code\Convergence-test.py 40 400 && python OAMCompare\Code\FBPIC_Image.py Conv_40_400 ^
&& rmdir /S /Q diags ^
&& python OAMCompare\Code\Convergence-test.py 50 500 && python OAMCompare\Code\FBPIC_Image.py Conv_50_500 ^
&& rmdir /S /Q diags ^
&& python OAMCompare\Code\Convergence-test.py 50 800 && python OAMCompare\Code\FBPIC_Image.py Conv_50_800 ^
&& rmdir /S /Q diags ^
&& python OAMCompare\Code\Convergence-test.py 100 1000 && python OAMCompare\Code\FBPIC_Image.py Conv_100_1000^
&& rmdir /S /Q diags ^
&& python OAMCompare\Code\Convergence-test.py 200 1000 && python OAMCompare\Code\FBPIC_Image.py Conv_200_1000