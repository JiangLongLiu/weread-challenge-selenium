#!/bin/bash
# account-4735 定时任务配置脚本
# 使用方式: bash scripts/setup-cron.sh

WORK_DIR="/mnt/sata1-1/docker/mycontainers/weread-challenge-selenium"

echo "=========================================="
echo "account-4735 定时任务配置"
echo "=========================================="

# 检查目录是否存在
if [ ! -d "$WORK_DIR" ]; then
    echo "错误: 工作目录不存在: $WORK_DIR"
    exit 1
fi

# 添加定时任务 (每6小时执行一次: 0,6,12,18点)
CRON_CMD="0 */6 * * * cd $WORK_DIR && docker compose up -d"

# 检查是否已存在
if crontab -l 2>/dev/null | grep -q "account-4735"; then
    echo "定时任务已存在，先删除..."
    crontab -l 2>/dev/null | grep -v "account-4735" | crontab -
fi

# 添加新任务
(crontab -l 2>/dev/null; echo "# account-4735 微信读书定时任务") | crontab -
(crontab -l 2>/dev/null; echo "$CRON_CMD") | crontab -

echo "定时任务已添加:"
crontab -l | grep "account-4735"

echo ""
echo "=========================================="
echo "当前定时任务:"
crontab -l
echo "=========================================="
