#!/usr/bin/env python3
"""
拉取 v0.15.0 镜像
"""

import pandas as pd
import paramiko

PASSWORD_FILE = r'E:\Qoder_workspace\weread-challenge-selenium\docs\rk3566-muti-user-deploy\password.xls'

def get_credentials():
    df = pd.read_excel(PASSWORD_FILE)
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
    print("拉取 v0.15.0 镜像")
    print("=" * 60)
    
    cmd = 'docker pull jqknono/weread-challenge:v0.15.0'
    print(f"执行: {cmd}")
    print("这可能需要几分钟...\n")
    
    stdin, stdout, stderr = client.exec_command(cmd)
    exit_code = stdout.channel.recv_exit_status()
    
    stdout_data = stdout.read().decode()
    stderr_data = stderr.read().decode()
    
    if stdout_data:
        print(stdout_data)
    if stderr_data:
        print("错误:", stderr_data)
    
    print(f"\n退出码: {exit_code}")
    
    if exit_code == 0:
        print("\n镜像拉取成功！")
        # 验证镜像
        print("\n验证镜像...")
        stdin, stdout, stderr = client.exec_command('docker images | grep weread-challenge')
        result = stdout.read().decode().strip()
        print(result)
    else:
        print("\n镜像拉取失败！")
    
    client.close()
    print("=" * 60)

if __name__ == "__main__":
    main()
