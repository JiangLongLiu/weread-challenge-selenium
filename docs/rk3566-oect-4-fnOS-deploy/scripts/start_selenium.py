#!/usr/bin/env python3
"""手动启动 selenium"""

import pandas as pd
import paramiko
import time

PASSWORD_FILE = r'E:\Qoder_workspace\weread-challenge-selenium\docs\rk3566-oect-4-fnOS-deploy\password.csv'

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

    print("=== 启动 selenium ===")
    cmd = 'cd /vol1/docker/mycontainers/weread-challenge-selenium-muti-user && docker compose up -d selenium'
    stdin, stdout, stderr = client.exec_command(cmd)
    result = stdout.read().decode().strip()
    err = stderr.read().decode().strip()

    print("stdout:", result)
    if err:
        print("stderr:", err)

    time.sleep(5)

    print("\n=== 检查容器 ===")
    stdin, stdout, stderr = client.exec_command('docker ps --format "{{.Names}} {{.Status}}"')
    result = stdout.read().decode().strip()
    print(result)

    client.close()

if __name__ == "__main__":
    main()
