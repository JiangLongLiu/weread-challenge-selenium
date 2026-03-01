#!/usr/bin/env python3
"""
简化测试 Xvfb 启动
"""

import pandas as pd
import paramiko
import time

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
    print("简化测试 Xvfb 启动")
    print("=" * 60)
    
    # 尝试最简单的 Xvfb 启动
    print("\n【1. 最简单的方式启动 Xvfb】")
    stdin, stdout, stderr = client.exec_command('docker exec weread-challenge-selenium-muti-user-selenium-1 Xvfb :99 -screen 0 1920x1080x24 &')
    stdout.channel.recv_exit_status()
    time.sleep(2)
    
    # 检查是否启动成功
    print("\n【2. 检查 Xvfb 进程】")
    stdin, stdout, stderr = client.exec_command('docker exec weread-challenge-selenium-muti-user-selenium-1 ps aux | grep Xvfb')
    result = stdout.read().decode().strip()
    print(result if result else "Xvfb 未运行")
    
    # 检查 99 号显示
    print("\n【3. 检查 X11 socket】")
    stdin, stdout, stderr = client.exec_command('docker exec weread-challenge-selenium-muti-user-selenium-1 ls -la /tmp/.X11-unix/ 2>/dev/null || echo "目录不存在"')
    result = stdout.read().decode().strip()
    print(result)
    
    # 检查错误
    print("\n【4. 检查 Xvfb 错误】")
    stdin, stdout, stderr = client.exec_command('docker exec weread-challenge-selenium-muti-user-selenium-1 bash -c "Xvfb :99 -screen 0 1920x1080x24 2>&1 & sleep 2; ps aux | grep Xvfb"')
    result = stdout.read().decode().strip()
    print(result)
    
    client.close()
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
