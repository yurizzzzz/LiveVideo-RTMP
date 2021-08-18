import time
import cv2
import subprocess
import multiprocessing as mp


def rtmp():
    subprocess.run(
        'gst-launch-1.0 -e nvarguscamerasrc sensor-id=0 ! "video/x-raw(memory:NVMM),width=1920,height=1080,framerate=30/1" ! nvv4l2h264enc ! queue ! h264parse ! flvmux ! rtmpsink location="rtmp://47.104.88.125:1935/rtmplive" -e',
        shell=True)


p = mp.Process(target=rtmp)
p.start()
