#!/usr/bin/env python3
"""检查定时任务"""
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(hostname='192.168.123.54', port=22, username='root', password='1234567890')

print("=" * 60)
print("检查定时任务")
print("=" * 60)

# 检查完整的 crontab
stdin, stdout, stderr = ssh.exec_command('crontab -l')
output = stdout.read().decode()
print("\n完整 Crontab:")
print(output)

# 只查看任务行（非注释）
stdin, stdout, stderr = ssh.exec_command('crontab -l 2>/dev/null | grep -v "^#" | grep -v "^$"')
tasks = stdout.read().decode()
print("\n任务行:")
print(tasks if tasks else "无任务")

ssh.close()
