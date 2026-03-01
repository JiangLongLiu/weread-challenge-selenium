#!/usr/bin/env python3
"""
手动启动 app-1 并调试
"""

import pandas as pd
import paramiko

PASSWORD_FILE = r'E:\Qoder_workspace\weread-challenge-selenium\docs\rk3566-muti-user-deploy\password.csv'

def get_credentials():
    df = pd.read_csv(PASSWORD_FILE)
    row = df.iloc[0]
    return {
        'host': str(row['IP地址']).strip(),
        'port': int(row['SSH端口']),
        'username': str(row['用户名']).strip(),
        'password': str(row['密码']).strip()
    }

def main():
    cred = get_credentials()
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(
        hostname=cred['host'],
        port=cred['port'],
        username=cred['username'],
        password=cred['password']
    )
    
    print("=" * 60)
    print("手动启动 app-1 调试")
    print("=" * 60)
    
    # 步骤1: 手动启动 app-1
    print("\n【步骤1】手动启动 app-1")
    cmd = 'cd /mnt/sata1-1/docker/mycontainers/weread-challenge-selenium-muti-user && docker compose up app-1 -d'
    stdin, stdout, stderr = client.exec_command(cmd)
    exit_code = stdout.channel.recv_exit_status()
    stdout_data = stdout.read().decode()
    stderr_data = stderr.read().decode()
    
    print(f"命令: {cmd}")
    print(f"退出码: {exit_code}")
    if stdout_data:
        print(f"输出:\n{stdout_data}")
    if stderr_data:
        print(f"错误:\n{stderr_data}")
    
    # 步骤2: 检查容器状态
    print("\n【步骤2】检查容器状态")
    stdin, stdout, stderr = client.exec_command('docker ps -a | grep app-1')
    result = stdout.read().decode().strip()
    if result:
        print(result)
    else:
        print("无 app-1 容器")
    
    # 步骤3: 查看容器日志
    print("\n【步骤3】查看容器日志")
    stdin, stdout, stderr = client.exec_command('docker logs weread-challenge-selenium-muti-user-app-1-1 2>&1 | tail -30')
    logs = stdout.read().decode().strip()
    if logs:
        print(logs)
    else:
        print("无日志或容器不存在")
    
    # 步骤4: 检查数据目录
    print("\n【步骤4】检查 liujl4735 数据目录")
    stdin, stdout, stderr = client.exec_command('ls -la /mnt/sata1-1/docker/mycontainers/weread-challenge-selenium-muti-user/data/liujl4735/')
    result = stdout.read().decode().strip()
    print(result if result else "目录不存在")
    
    client.close()
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
