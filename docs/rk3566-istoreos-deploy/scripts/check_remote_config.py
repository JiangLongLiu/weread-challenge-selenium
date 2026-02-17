import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('192.168.123.51', 22, 'root', '1234567890')

# 检查远程 docker-compose.yml 内容
print("=== 远程 docker-compose.yml 内容 ===")
stdin, stdout, stderr = client.exec_command('cat /mnt/sata1-1/docker/mycontainers/weread-challenge-selenium/docker-compose.yml')
print(stdout.read().decode())

# 检查所有环境变量
print("\n=== selenium 容器所有环境变量 ===")
stdin, stdout, stderr = client.exec_command('docker inspect weread-challenge-selenium-selenium-1 --format="{{range .Config.Env}}{{println .}}{{end}}"')
print(stdout.read().decode())

client.close()
