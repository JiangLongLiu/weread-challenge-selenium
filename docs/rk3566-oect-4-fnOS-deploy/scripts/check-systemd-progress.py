#!/usr/bin/env python3
"""检查 systemd 服务启动进度"""
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(hostname='192.168.123.54', port=22, username='root', password='1234567890')

print("=" * 80)
print("检查 systemd 服务启动进度")
print("=" * 80)

# 1. 检查 systemd 服务状态
print("\n【1. systemd 服务状态】")
stdin, stdout, stderr = ssh.exec_command('systemctl status weread-selenium.service')
result = stdout.read().decode().strip()
print(result)

# 2. 检查 systemd 日志（完整）
print("\n【2. systemd 启动日志】")
stdin, stdout, stderr = ssh.exec_command('journalctl -u weread-selenium.service --since boot | tail -50')
result = stdout.read().decode().strip()
print(result)

# 3. 检查当前时间
print("\n【3. 当前系统时间】")
stdin, stdout, stderr = ssh.exec_command('date')
result = stdout.read().decode().strip()
print(result)

# 4. 检查系统启动时间
print("\n【4. 系统启动时间】")
stdin, stdout, stderr = ssh.exec_command('uptime -s')
result = stdout.read().decode().strip()
print(result)

# 5. 检查 Docker 容器（所有）
print("\n【5. 所有 Docker 容器】")
stdin, stdout, stderr = ssh.exec_command('docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Image}}" | head -20')
result = stdout.read().decode().strip()
print(result)

# 6. 检查 docker compose 进程
print("\n【6. docker compose 进程】")
stdin, stdout, stderr = ssh.exec_command('ps aux | grep "docker compose" | grep -v grep')
result = stdout.read().decode().strip()
print(result if result else "无 docker compose 进程")

# 7. 检查 selenium 相关进程
print("\n【7. selenium 相关进程】")
stdin, stdout, stderr = ssh.exec_command('ps aux | grep selenium | grep -v grep')
result = stdout.read().decode().strip()
print(result if result else "无 selenium 进程")

print("\n" + "=" * 80)
print("检查完成")
print("=" * 80)

ssh.close()
