import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('192.168.123.51', 22, 'root', '1234567890')

# 检查 selenium 容器的环境变量
print("检查 selenium 容器环境变量...")
stdin, stdout, stderr = client.exec_command('docker inspect weread-challenge-selenium-selenium-1 --format="{{json .Config.Env}}"')
import json
envs = json.loads(stdout.read().decode())
for env in envs:
    if 'VNC' in env or 'PASSWORD' in env:
        print(env)

# 检查日志
print("\n--- selenium 容器日志 ---")
stdin, stdout, stderr = client.exec_command('docker logs weread-challenge-selenium-selenium-1 --tail 20')
print(stdout.read().decode())

client.close()
