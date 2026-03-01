#!/usr/bin/env python3
"""
检查开机启动日志
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
    print("开机启动日志检查")
    print("=" * 60)

    # 检查系统启动时间
    print("\n【1. 系统启动时间】")
    stdin, stdout, stderr = client.exec_command('uptime -s')
    result = stdout.read().decode().strip()
    print(result)

    # 检查容器启动时间
    print("\n【2. Selenium 容器启动时间】")
    stdin, stdout, stderr = client.exec_command('docker ps --format "{{.Names}} {{.Status}}" | grep selenium')
    result = stdout.read().decode().strip()
    print(result)

    # 检查 weread-selenium 启动日志
    print("\n【3. weread-selenium 启动日志】")
    stdin, stdout, stderr = client.exec_command('logread | grep -i weread | tail -10')
    result = stdout.read().decode().strip()
    print(result if result else "无日志")

    # 检查 X11 清理相关日志
    print("\n【4. X11 清理日志】")
    stdin, stdout, stderr = client.exec_command('logread | grep -i "Cleaned\|X11" | tail -5')
    result = stdout.read().decode().strip()
    print(result if result else "无日志")

    client.close()
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
