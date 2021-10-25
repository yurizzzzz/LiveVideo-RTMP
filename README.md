# LiveVideo-RTMP

在云服务器端采用nginx+rtmp的形式来搭建流媒体服务器，客户端通过ffmpeg或者gstreamer进行推流，视频流的传输协议是rtmp协议，当然还有其他各种协议但是从稳定性和传输效率来讲rtmp协议比较适合而且微信小程序仅支持RTMP协议的实时视频流传输。

# Environment
- subprocess
- threading
- queue
- cv2

# How to Start
## 在云服务器上配置nginx+rtmp流媒体服务
- 安装nginx和nginx-rtmp-module的依赖
```
sudo apt-get install build-essential libpcre3 libpcre3-dev libssl-dev
sudo apt-get install zlib1g
sudo apt-get install zlib1g-dev
```
- 下载nginx和nginx-rtmp-module的源码
```
wget http://nginx.org/download/nginx-1.18.0.tar.gz
tar -zxvf nginx-1.18.0.tar.gz
git clone https://github.com/arut/nginx-rtmp-module.git
```
- 编译安装nginx
```
cd nginx
./configure --add-module=../nginx-rtmp-module --with-http_ssl_module #将rtmp模块编译到nginx
make
make install
```
- 将nginx加入系统控制中
```
cd /usr/lib/systemd/
sudo mkdir system 
cd system
sudo touch nginx.service
sudo gedit nginx.service
```
- 添加以下内容
```
[Unit]

Description=nginx - high performance web server
Documentation=http://nginx.org/en/docs/
After=network.target remote-fs.target nss-lookup.target
 
[Service]
 
Type=forking
WorkingDirectory=/usr/local/nginx         
ExecStart=/usr/local/nginx/sbin/nginx  
ExecReload=/bin/kill -s HUP $MAINPID
ExecStop=/bin/kill -s QUIT $MAINPID
PrivateTmp=true
 
[Install]
 
WantedBy=multi-user.target

```
- 使文件生效
```
sudo systemctl daemon-reload
```
- 在后台开启nginx
```
sudo systemctl start nginx
```
- 配置RTMP协议
```
cd /usr/local/nginx/conf/
sudo gedit nginx.conf
sudo gedit nginx.conf.default
```
- 两个文件都添加rtmp协议及监听的端口
```
rtmp {
    server {
        listen 1935;

        application rtmplive {
            live on;
            max_connections 1024;
        }
    }
}
```
- 重启nginx服务
```
sudo systemctl restart nginx
```
- 在云服务器的安全组里添加1935端口

## 启用摄像头进行推流(这里仅做CSI摄像头推流，USB摄像头类似)

- 使用ffmpeg进行推流
```
python ffmpeg.py
# 由于Jetson nano上无法进行ffmpeg硬编码因此只能使用软编码，编码方式是H264编码，直播延迟在8秒左右
```
- 使用Gstreamer进行推流
```
python gstreamer.py
# Gstreamer是jetson nano自带的一个流媒体框架，可以实现使用jetson nano的GPU进行硬编码
# 直播延迟在5秒左右，整体上硬编码的稳定性比软编码要好很多
```