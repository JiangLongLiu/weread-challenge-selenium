import paramiko
import time

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('192.168.123.51', 22, 'root', '1234567890')

# 重启 selenium 容器使 VNC 密码生效
print('重启 selenium 容器...')
stdin, stdout, stderr = client.exec_command('docker restart weread-challenge-selenium-selenium-1')
print('STDOUT:', stdout.read().decode())

time.sleep(5)

# 检查容器状态
stdin, stdout, stderr = client.exec_command('docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"')
print('\n容器状态:')
print(stdout.read().decode())

client.close()
