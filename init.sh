#!/usr/bin/env bash


basepath=$(cd `dirname $0`; pwd)


sudo docker stop power;
sudo docker rm power;

sudo docker run -it \
        -p 6080:6080 \
        --restart always \
        --privileged \
        -v $basepath:/mnt/power \
        --name power binbinxm:0.1 /bin/bash \
        -c "cd /mnt/power;/opt/conda/bin/python3 init.py"
