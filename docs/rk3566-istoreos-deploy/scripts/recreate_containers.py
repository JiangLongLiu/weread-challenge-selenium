import paramiko
import time
import json

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('192.168.123.51', 22, 'root', '1234567890')

# 删除旧容器
print("删除旧容器...")
stdin, stdout, stderr = client.exec_command('cd /mnt/sata1-1/docker/mycontainers/weread-challenge-selenium && docker compose down')
print('STDOUT:', stdout.read().decode())
print('STDERR:', stderr.read().decode())

# 重新创建并启动
print("\n重新启动容器...")
stdin, stdout, stderr = client.exec_command('cd /mnt/sata1-1/docker/mycontainers/weread-challenge-selenium && docker compose up -d')
print('STDOUT:', stdout.read().decode())
print('STDERR:', stderr.read().decode())

# 等待容器启动
time.sleep(10)

# 检查容器状态
print("\n检查容器状态...")
stdin, stdout, stderr = client.exec_command('docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"')
print(stdout.read().decode())

# 检查环境变量
print("\n检查 selenium 容器环境变量...")
stdin, stdout, stderr = client.exec_command('docker inspect weread-challenge-selenium-selenium-1 --format="{{json .Config.Env}}"')
envs = json.loads(stdout.read().decode())
for env in envs:
    if 'VNC' in env or 'PASSWORD' in env:
        print(env)

client.close()
