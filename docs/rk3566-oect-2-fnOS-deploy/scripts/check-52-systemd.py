#!/usr/bin/env python3
"""检查 192.168.123.52 主机的 systemd 服务配置"""
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(hostname='192.168.123.52', port=22, username='root', password='1234567890')

print("=" * 80)
print("检查 192.168.123.52 (RK3566-OECT1-2-fnOS) systemd 服务配置")
print("=" * 80)

# 1. 检查 systemd 服务状态
print("\n【1. systemd 服务状态】")
stdin, stdout, stderr = ssh.exec_command('systemctl status weread-selenium.service | head -20')
result = stdout.read().decode().strip()
print(result)

# 2. 检查服务启用状态
print("\n【2. 服务启用状态】")
stdin, stdout, stderr = ssh.exec_command('systemctl is-enabled weread-selenium.service')
result = stdout.read().decode().strip()
print(f"启用状态：{result}")

# 3. 检查 systemd 服务文件
print("\n【3. systemd 服务文件内容】")
stdin, stdout, stderr = ssh.exec_command('cat /etc/systemd/system/weread-selenium.service')
result = stdout.read().decode().strip()
print(result if result else "文件不存在")

# 4. 检查开机启动脚本
print("\n【4. /etc/init.d/weread-selenium】")
stdin, stdout, stderr = ssh.exec_command('ls -la /etc/init.d/weread-selenium 2>&1')
result = stdout.read().decode().strip()
print(result if result else "文件不存在")

# 5. 检查容器状态
print("\n【5. 容器状态】")
stdin, stdout, stderr = ssh.exec_command('docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Image}}" | grep -E "selenium|weread"')
result = stdout.read().decode().strip()
print(result if result else "无运行中的容器")

# 6. 检查系统日志
print("\n【6. systemd 启动日志】")
stdin, stdout, stderr = ssh.exec_command('journalctl -u weread-selenium.service --since boot | tail -20')
result = stdout.read().decode().strip()
print(result if result else "无日志")

print("\n" + "=" * 80)
print("检查完成")
print("=" * 80)

ssh.close()
