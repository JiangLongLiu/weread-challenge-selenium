#!/usr/bin/env python3
"""验证容器启动状态"""
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(hostname='192.168.123.54', port=22, username='root', password='1234567890')

print("=" * 80)
print("验证容器启动状态")
print("=" * 80)

# 1. 检查 systemd 服务状态
print("\n【1. systemd 服务状态】")
stdin, stdout, stderr = ssh.exec_command('systemctl status weread-selenium.service')
result = stdout.read().decode().strip()
print(result)

# 2. 检查容器状态
print("\n【2. 容器状态】")
stdin, stdout, stderr = ssh.exec_command('cd /vol1/docker/mycontainers/weread-challenge-selenium-muti-user && docker compose ps')
result = stdout.read().decode().strip()
if result:
    print(result)
    print("\n✅ 容器已启动！")
else:
    print("无运行中的容器")
    print("⚠ 容器可能还在启动中...")

# 3. 检查 Selenium 容器详情
print("\n【3. Selenium 容器详情】")
stdin, stdout, stderr = ssh.exec_command('docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep selenium')
result = stdout.read().decode().strip()
if result:
    print(result)
    print("\n✅ Selenium 容器运行正常！")
else:
    print("Selenium 容器未运行")
    print("⚠ 请等待 180 秒启动时间完成")

# 4. 检查所有容器（包括已退出的）
print("\n【4. 所有 Docker 容器】")
stdin, stdout, stderr = ssh.exec_command('docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Image}}" | grep -E "selenium|weread"')
result = stdout.read().decode().strip()
print(result if result else "无 weread/selenium 相关容器")

# 5. 检查 systemd 日志
print("\n【5. systemd 启动日志（最后 20 行）】")
stdin, stdout, stderr = ssh.exec_command('journalctl -u weread-selenium.service --since boot | tail -20')
result = stdout.read().decode().strip()
print(result if result else "无日志")

# 6. 检查当前时间
print("\n【6. 当前系统时间】")
stdin, stdout, stderr = ssh.exec_command('date')
result = stdout.read().decode().strip()
print(result)

# 7. 检查系统启动时间
print("\n【7. 系统启动时间】")
stdin, stdout, stderr = ssh.exec_command('uptime -s')
result = stdout.read().decode().strip()
print(f"系统启动时间：{result}")

# 计算启动后经过的时间
from datetime import datetime
try:
    boot_time = datetime.strptime(result, '%Y-%m-%d %H:%M:%S')
    now = datetime.now()
    # fnOS 时间可能是 UTC，需要转换
    elapsed = (now - boot_time).total_seconds()
    print(f"启动后经过时间：约 {elapsed/60:.1f} 分钟")
except:
    pass

print("\n" + "=" * 80)
print("验证完成")
print("=" * 80)

ssh.close()
