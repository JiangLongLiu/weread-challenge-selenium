import paramiko
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('192.168.123.51', 22, 'root', '1234567890')

# 手动启动 app 容器，绕过依赖检查
print("启动 app 容器...")
stdin, stdout, stderr = client.exec_command('docker start weread-challenge-selenium-app-1')
print('STDOUT:', stdout.read().decode())
print('STDERR:', stderr.read().decode())

# 等待几秒
import time
time.sleep(5)

# 检查容器状态
print("\n检查容器状态...")
stdin, stdout, stderr = client.exec_command('docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"')
print(stdout.read().decode())

# 检查 data 目录
print("\ndata 目录内容...")
stdin, stdout, stderr = client.exec_command('ls -la /mnt/sata1-1/docker/mycontainers/weread-challenge-selenium/data/')
print(stdout.read().decode())

# 检查 app 日志
print("\n--- app 容器日志 ---")
stdin, stdout, stderr = client.exec_command('docker logs weread-challenge-selenium-app-1 --tail 20')
print(stdout.read().decode())
print(stderr.read().decode())

client.close()
