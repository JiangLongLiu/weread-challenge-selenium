#!/usr/bin/env python3
# -*- coding: utf-8 -*-
content = """#!/bin/sh
# WeRead Selenium Auto Start - 标准 init.d 脚本

NAME="weread-selenium"
DESC="WeRead Selenium Container"
DIR="/mnt/sata1-1/docker/mycontainers/weread-challenge-selenium-muti-user"

start() {
    echo "Starting $DESC..."
    /etc/init.d/cron start
    echo "Waiting 180 seconds for system to stabilize..."
    sleep 180
    while ! docker ps >/dev/null 2>&1; do
        sleep 2
    done
    rm -f /tmp/.X*-lock /tmp/.X11-unix/X* 2>/dev/null
    echo "Cleaned up old X11 resources"
    cd "$DIR" && docker compose up -d selenium
    echo "$NAME started"
}

stop() {
    echo "Stopping $DESC..."
    cd "$DIR" && docker compose down
    echo "$NAME stopped"
}

case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        stop
        sleep 5
        start
        ;;
    *)
        echo "Usage: $0 {start|stop|restart}"
        exit 1
        ;;
esac

exit 0
"""
with open(r'e:\Qoder_workspace\weread-challenge-selenium\docs\rk3566-muti-user-deploy\scripts\工具\weread-selenium.init', 'w', encoding='utf-8') as f:
    f.write(content)
print('Done')
