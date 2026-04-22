#!/usr/bin/env python3
"""
拉取 weread-challenge 镜像
自动从 docker-compose.yml 读取镜像版本
"""

import os
import pandas as pd
import paramiko
import yaml

PASSWORD_FILE = r'E:\Qoder_workspace\weread-challenge-selenium\docs\rk3566-oect-4-fnOS-deploy\password.csv'
COMPOSE_FILE = r'E:\Qoder_workspace\weread-challenge-selenium\docs\rk3566-oect-4-fnOS-deploy\docker-compose.yml'

def get_credentials():
    df = pd.read_csv(PASSWORD_FILE)
    row = df.iloc[0]
    return {
        'host': str(row['IP地址']).strip(),
        'port': int(row['SSH端口']),
        'username': str(row['用户名']).strip(),
        'password': str(row['密码']).strip()
    }

def get_image_version():
    """从 docker-compose.yml 读取镜像版本"""
    with open(COMPOSE_FILE, 'r', encoding='utf-8') as f:
        compose = yaml.safe_load(f)

    # 读取 app-1 的镜像
    image = compose['services']['app-1']['image']
    # 提取版本号（格式：jqknono/weread-challenge:v0.15.0）
    version = image.split(':')[-1]
    return image, version

def main():
    cred = get_credentials()
    image, version = get_image_version()

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(
        hostname=cred['host'],
        port=cred['port'],
        username=cred['username'],
        password=cred['password']
    )

    print("=" * 60)
    print(f"拉取 {image} 镜像")
    print("=" * 60)

    cmd = f'docker pull {image}'
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
