@echo off
chcp 65001
set PYTHONUSERBASE=.\python\Lib\site-packages
set PYTHONPATH=.\python\Lib\site-packages
set PATH=%PATH%;.\python\Scripts
cd wav2lip
..\python\python.exe genavatar.py --video_path ../video/08.mp4 --img_size 384 --avatar_id avatar08 --face_det_batch_size 4
pause