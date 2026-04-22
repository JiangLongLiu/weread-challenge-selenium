#!/usr/bin/env python3
"""检查 VNC 状态"""
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(hostname='192.168.123.54', port=22, username='root', password='1234567890')

print("=" * 80)
print("VNC 状态检查")
print("=" * 80)

# 1. 检查容器内端口监听
print("\n【1. 容器内端口监听】")
stdin, stdout, stderr = ssh.exec_command('docker exec weread-challenge-selenium-muti-user netstat -tlnp 2>/dev/null | grep -E "7900|5900"')
result = stdout.read().decode().strip()
print(result if result else "端口未监听")

# 2. 检查 VNC 进程
print("\n【2. VNC 进程】")
stdin, stdout, stderr = ssh.exec_command('docker exec weread-challenge-selenium-muti-user ps aux | grep -i vnc | grep -v grep')
result = stdout.read().decode().strip()
print(result if result else "无 VNC 进程")

# 3. 检查 VNC 日志
print("\n【3. VNC 日志】")
stdin, stdout, stderr = ssh.exec_command('docker logs weread-challenge-selenium-muti-user 2>&1 | grep -i "vnc\|noVNC" | tail -15')
result = stdout.read().decode().strip()
print(result if result else "无 VNC 日志")

# 4. 检查环境变量
print("\n【4. VNC 环境变量】")
stdin, stdout, stderr = ssh.exec_command('docker exec weread-challenge-selenium-muti-user env | grep -i vnc')
result = stdout.read().decode().strip()
print(result if result else "无 VNC 环境变量")

# 5. 检查 noVNC 进程
print("\n【5. noVNC 进程】")
stdin, stdout, stderr = ssh.exec_command('docker exec weread-challenge-selenium-muti-user ps aux | grep -i novnc | grep -v grep')
result = stdout.read().decode().strip()
print(result if result else "无 noVNC 进程")

# 6. 检查所有监听端口
print("\n【6. 容器内所有监听端口】")
stdin, stdout, stderr = ssh.exec_command('docker exec weread-challenge-selenium-muti-user netstat -tlnp')
result = stdout.read().decode().strip()
print(result)

print("\n" + "=" * 80)
print("检查完成")
print("=" * 80)

ssh.close()
