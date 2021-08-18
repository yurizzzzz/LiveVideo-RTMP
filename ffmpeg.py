import queue
import threading
import cv2 as cv
import subprocess as sp

# gst-launch-1.0 -e nvarguscamerasrc sensor-id=0 ! "video/x-raw(memory:NVMM),width=1920,height=1080,framerate=30/1" ! nvv4l2h264enc ! queue ! h264parse ! flvmux ! rtmpsink location='rtmp://47.104.88.125:1935/rtmplive'

class Live(object):
    def __init__(self):
        self.frame_queue = queue.Queue()
        self.command = ""
        # 设置RTMP推流地址
        self.rtmpUrl = 'rtmp://47.104.88.125:1935/rtmplive'
        # 读取CSI摄像头
        self.camera_path = ('nvarguscamerasrc ! '
                   'video/x-raw(memory:NVMM), '
                   'width=(int)1920, height=(int)1080, '
                   'format=(string)RG10, framerate=(fraction)40/1 ! '
                   'nvvidconv flip-method=2 ! '
                   'video/x-raw, width=(int){}, height=(int){}, '
                   'format=(string)BGRx ! '
                   'videoconvert ! appsink').format(1920, 1080)

    # 读取摄像头帧
    def read_frame(self):
        print("read frame")
        cap = cv.VideoCapture(self.camera_path, cv.CAP_GSTREAMER)
        # cap = cv.VideoCapture(0)
        
        # 启用终端命令
        self.command = ['ffmpeg',
                        '-y',
                        '-f', 'rawvideo',
                        '-vcodec', 'rawvideo',
                        '-pix_fmt', 'bgr24',
                        '-s', "{}x{}".format(1280, 720),
                        '-r', '30',
                        '-i', '-',
                        '-c:v', 'libx264',
                        '-pix_fmt', 'yuv420p',
                        '-preset', 'ultrafast',
                        '-f', 'flv',
                        self.rtmpUrl]

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # 将帧放入队列中
            self.frame_queue.put(frame)

    def push_frame(self):
        print('push frame')
        while True:
            if len(self.command) > 0:
                # 配置管道
                p = sp.Popen(self.command, stdin=sp.PIPE)
                break

        while True:
            if not self.frame_queue.empty():
                # 从队列中取出帧并放到ffmpeg要推流的管道中去
                frame = self.frame_queue.get()
                p.stdin.write(frame.tostring())

    def run(self):
        # 利用多线程让读取摄像头帧和推流同时进行减少卡顿
        threads = [
            threading.Thread(target=Live.read_frame, args=(self,)),
            threading.Thread(target=Live.push_frame, args=(self,))
        ]
        [thread.start() for thread in threads]


if __name__ == '__main__':
    live = Live()
    live.run()
