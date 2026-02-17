import paramiko
import os

# 本地文件路径
LOCAL_FILE = r'E:\Qoder_workspace\weread-challenge-selenium\docs\rk3566-istoreos-deploy\docker-compose.yml'
REMOTE_FILE = '/mnt/sata1-1/docker/mycontainers/weread-challenge-selenium/docker-compose.yml'

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('192.168.123.51', 22, 'root', '1234567890')

# 读取本地文件内容
with open(LOCAL_FILE, 'r', encoding='utf-8') as f:
    local_content = f.read()

print("=== 本地 docker-compose.yml 内容 ===")
print(local_content)

# 直接通过 SSH 写入文件
print("\n=== 写入远程文件 ===")
# 使用 cat 和 heredoc 写入文件
cmd = f'''cat > {REMOTE_FILE} << 'EOFMARKER'
{local_content}
EOFMARKER'''
stdin, stdout, stderr = client.exec_command(cmd)
print("STDERR:", stderr.read().decode())

# 验证远程文件
print("\n=== 验证远程文件 ===")
stdin, stdout, stderr = client.exec_command(f'cat {REMOTE_FILE}')
remote_content = stdout.read().decode()
print(remote_content)

# 删除容器并重新部署
print("\n=== 删除现有容器 ===")
stdin, stdout, stderr = client.exec_command('cd /mnt/sata1-1/docker/mycontainers/weread-challenge-selenium && docker compose down')
print(stderr.read().decode())

print("\n=== 重新启动容器 ===")
stdin, stdout, stderr = client.exec_command('cd /mnt/sata1-1/docker/mycontainers/weread-challenge-selenium && docker compose up -d')
import time
time.sleep(30)
print(stderr.read().decode())

# 检查容器状态
print("\n=== 容器状态 ===")
stdin, stdout, stderr = client.exec_command('docker ps --format "table {{.Names}}\\t{{.Status}}\\t{{.Ports}}" | grep weread')
print(stdout.read().decode())

# 检查环境变量
print("\n=== 检查 SE_VNC_PASSWORD 环境变量 ===")
stdin, stdout, stderr = client.exec_command('docker inspect weread-challenge-selenium-selenium-1 --format="{{range .Config.Env}}{{println .}}{{end}}" | grep VNC')
print(stdout.read().decode())

client.close()
