@echo off
chcp 65001
set PYTHONUSERBASE=.\python\Lib\site-packages
set PYTHONPATH=.\python\Lib\site-packages
set PATH=%PATH%;.\python\Scripts
.\python\python.exe funasr/funasr_wss_server.py
pause