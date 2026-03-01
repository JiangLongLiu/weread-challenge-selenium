#!/bin/sh
# /etc/init.d/weread-selenium
# 微信读书 Selenium 容器开机启动脚本

START=99
STOP=10

WORK_DIR="/mnt/sata1-1/docker/mycontainers/weread-challenge-selenium-oect1"

check_docker() {
    while ! docker ps >/dev/null 2>&1; do
        sleep 2
    done
}

boot() {
    check_docker
    cd "$WORK_DIR" && docker compose up -d selenium
}

shutdown() {
    cd "$WORK_DIR" && docker compose down
}

case "$1" in
    start|boot)
        boot
        ;;
    stop|shutdown)
        shutdown
        ;;
    restart)
        shutdown
        boot
        ;;
    *)
        echo "Usage: $0 {start|stop|restart}"
        exit 1
        ;;
esac
