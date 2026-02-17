import paramiko
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('192.168.123.51', 22, 'root', '1234567890')

# 检查容器状态
stdin, stdout, stderr = client.exec_command('docker ps -a --format "table {{.Names}}\t{{.Status}}"')
print('容器状态:')
print(stdout.read().decode())

# 检查 data 目录
stdin, stdout, stderr = client.exec_command('ls -la /mnt/sata1-1/docker/mycontainers/weread-challenge-selenium/data/')
print('\ndata目录内容:')
print(stdout.read().decode())

# 检查 app 容器日志
print('\n--- app 容器日志 ---')
stdin, stdout, stderr = client.exec_command('docker logs weread-challenge-selenium-app-1 --tail 30 2>&1')
print(stdout.read().decode())
print(stderr.read().decode())

client.close()
