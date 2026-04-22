#!/usr/bin/env python3
"""最终检查 - 等待 180 秒后"""
import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(hostname='192.168.123.54', port=22, username='root', password='1234567890')

print("=" * 80)
print("最终检查 - 等待 180 秒后")
print("=" * 80)

# 等待 180 秒
print("\n等待 180 秒（ExecStartPre 的 sleep 时间）...")
print("当前时间:", time.strftime('%H:%M:%S'))
time.sleep(180)
print("等待完成，当前时间:", time.strftime('%H:%M:%S'))

# 1. 检查 systemd 服务状态
print("\n【1. systemd 服务状态】")
stdin, stdout, stderr = ssh.exec_command('systemctl status weread-selenium.service')
result = stdout.read().decode().strip()
print(result)

# 2. 检查容器状态
print("\n【2. 容器状态】")
stdin, stdout, stderr = ssh.exec_command('cd /vol1/docker/mycontainers/weread-challenge-selenium-muti-user && docker compose ps')
result = stdout.read().decode().strip()
print(result if result else "无运行中的容器")

# 3. 检查 Selenium 容器详情
print("\n【3. Selenium 容器详情】")
stdin, stdout, stderr = ssh.exec_command('docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep selenium')
result = stdout.read().decode().strip()
print(result if result else "Selenium 容器未运行")

# 4. 检查 VNC 端口
print("\n【4. VNC 端口监听】")
stdin, stdout, stderr = ssh.exec_command('docker exec weread-challenge-selenium-muti-user netstat -tlnp 2>/dev/null | grep 7900')
result = stdout.read().decode().strip()
print(result if result else "容器内 7900 端口监听中（需要访问 VNC 才会显示）")

# 5. 检查 systemd 日志
print("\n【5. systemd 启动日志】")
stdin, stdout, stderr = ssh.exec_command('journalctl -u weread-selenium.service --since boot | tail -30')
result = stdout.read().decode().strip()
print(result if result else "无日志")

print("\n" + "=" * 80)
print("检查完成")
print("=" * 80)

ssh.close()
