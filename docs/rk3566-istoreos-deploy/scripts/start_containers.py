#!/usr/bin/env python3
"""部署容器脚本"""
import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('192.168.123.51', 22, 'root', '1234567890')

# 启动容器
print("正在拉取镜像...")
stdin, stdout, stderr = client.exec_command('cd /mnt/sata1-1/docker/mycontainers/weread-challenge-selenium && docker compose pull', timeout=600)
print('STDOUT:', stdout.read().decode())
print('STDERR:', stderr.read().decode())

print("\n正在启动容器...")
stdin, stdout, stderr = client.exec_command('cd /mnt/sata1-1/docker/mycontainers/weread-challenge-selenium && docker compose up -d', timeout=300)
print('STDOUT:', stdout.read().decode())
print('STDERR:', stderr.read().decode())

# 检查状态
print("\n检查容器状态...")
stdin, stdout, stderr = client.exec_command('docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"')
print(stdout.read().decode())

client.close()
print("\n部署完成!")
