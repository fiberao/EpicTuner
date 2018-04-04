rem @echo off
rem SET PYTHON=jupyter qtconsole 
rem set up environment, edit to match your system
call C:\Anaconda2\Scripts\activate.bat C:\Anaconda2\envs\py27_32
rem The name of python interpretator, edit to match to your system
SET PYTHON=python
rem Current version of the simulation script
SET SCRIPT=response8.py 
rem A sequence of calls to do perform calculations for different MMDM models, uncloment lines as neccessary
%PYTHON% %SCRIPT% --out=output\mmdm15-37\  --actuators=mmdm15-37_actuators.txt --vias=mmdm15-37_vias.txt --via_size=21 --max_stroke=8e-6 --linewidth=8
rem %PYTHON% %SCRIPT% --out=output\mmdm15-39\  --actuators=mmdm15-39_actuators.txt --vias=mmdm15-39_vias.txt --via_size=0 --size=15 --aperture=15 --max_stroke=9.4e-6 --linewidth=4
rem %PYTHON% %SCRIPT% --out=output\mmdm15-17\  --actuators=mmdm15-17_actuators.txt --vias=mmdm15-17_vias.txt --via_size=21 --max_stroke=8e-6 --linewidth=8
rem %PYTHON% %SCRIPT% --out=output\mmdm30-59\  --actuators=mmdm30-59_actuators.txt --vias=mmdm30-59_vias.txt --size=30 --aperture=30 --via_size=18 --max_stroke=9e-6 --linewidth=8
rem %PYTHON% %SCRIPT% -- --out=output\mmdm30-39\  --actuators=mmdm30-39_actuators.txt --vias=mmdm30-39_vias.txt --size=30 --aperture=30 --via_size=18 --max_stroke=9e-6 --linewidth=8
rem %PYTHON% %SCRIPT% --out=output\mmdm30-79\  --actuators=mmdm30-79_actuators.txt --vias=mmdm30-79_vias.txt --size=30 --aperture=30 --via_size=18 --max_stroke=9e-6 --linewidth=8
rem %PYTHON% %SCRIPT% --out output\mmdm40-59\  --actuators=mmdm40-59_actuators.txt --vias=mmdm40-59_vias.txt --size=40 --aperture=40 --via_size=21 --max_stroke=15e-6 --linewidth=8
rem %PYTHON% %SCRIPT% --out output\mmdm40-79\  --actuators=mmdm40-79_actuators.txt --vias=mmdm40-79_vias.txt --size=40 --aperture=40 --via_size=21 --max_stroke=15e-6 --linewidth=8
rem %PYTHON% %SCRIPT% --out output\mmdm50-79\  --actuators=mmdm50-79_actuators.txt --vias=mmdm50-79_vias.txt --size=50 --aperture=50 --via_size=21 --max_stroke=30e-6 --linewidth=8
rem %PYTHON% %SCRIPT% --out output\mdm96\  --actuators=mdm96_actuators.txt --vias=mdm96_vias.txt --size=25.4 --aperture=25.4 --via_size=12 --max_stroke=19e-6 --linewidth=8
