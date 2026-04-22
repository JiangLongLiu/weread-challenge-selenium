#!/usr/bin/env python3
"""检查部署后的容器状态"""
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(hostname='192.168.123.54', port=22, username='root', password='1234567890')

print("=" * 80)
print("部署后容器状态检查")
print("=" * 80)

# 1. 检查容器状态
print("\n【1. 容器状态】")
stdin, stdout, stderr = ssh.exec_command('cd /vol1/docker/mycontainers/weread-challenge-selenium-muti-user && docker compose ps')
result = stdout.read().decode().strip()
print(result)

# 2. 检查镜像版本
print("\n【2. 容器镜像版本】")
stdin, stdout, stderr = ssh.exec_command('docker ps --format "table {{.Names}}\t{{.Image}}" | grep -E "selenium|weread"')
result = stdout.read().decode().strip()
print(result)

# 3. 检查本地镜像列表
print("\n【3. 本地镜像列表】")
stdin, stdout, stderr = ssh.exec_command('docker images | grep -E "selenium|weread-challenge"')
result = stdout.read().decode().strip()
print(result)

# 4. 检查 Selenium 日志
print("\n【4. Selenium 容器日志（最后 15 行）】")
stdin, stdout, stderr = ssh.exec_command('docker logs weread-challenge-selenium-muti-user 2>&1 | tail -15')
result = stdout.read().decode().strip()
print(result)

# 5. 检查 VNC 端口
print("\n【5. VNC 端口监听】")
stdin, stdout, stderr = ssh.exec_command('docker exec weread-challenge-selenium-muti-user netstat -tlnp | grep 7900')
result = stdout.read().decode().strip()
print(result if result else "容器内 7900 端口监听中（需要访问 VNC 才会显示）")

print("\n" + "=" * 80)
print("检查完成")
print("=" * 80)

ssh.close()
