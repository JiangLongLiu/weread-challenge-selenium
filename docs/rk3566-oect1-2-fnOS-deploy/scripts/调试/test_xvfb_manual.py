#!/usr/bin/env python3
"""
手动测试 Xvfb 启动
"""

import pandas as pd
import paramiko

PASSWORD_FILE = r'E:\Qoder_workspace\weread-challenge-selenium\docs\rk3566-oect1-2-fnOS-deploy\password.csv'

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
    print("手动测试 Xvfb 启动")
    print("=" * 60)
    
    # 检查环境变量
    print("\n【1. 检查 DISPLAY 环境变量】")
    stdin, stdout, stderr = client.exec_command('docker exec selenium-weread-challenge-selenium-oect1 env | grep DISPLAY')
    result = stdout.read().decode().strip()
    print(result)
    
    # 手动运行 xvfb-run 查看详细错误
    print("\n【2. 手动运行 xvfb-run】")
    cmd = 'docker exec selenium-weread-challenge-selenium-oect1 xvfb-run --server-num=99 --listen-tcp --server-args="-screen 0 1920x1080x24" echo test 2>&1'
    stdin, stdout, stderr = client.exec_command(cmd)
    result = stdout.read().decode().strip()
    print(result)
    
    # 检查 Xvfb 是否可用
    print("\n【3. 检查 Xvfb 版本】")
    stdin, stdout, stderr = client.exec_command('docker exec selenium-weread-challenge-selenium-oect1 Xvfb -version 2>&1 | head -2')
    result = stdout.read().decode().strip()
    print(result)
    
    # 检查 /var/tmp 是否存在
    print("\n【4. 检查 /var/tmp】")
    stdin, stdout, stderr = client.exec_command('docker exec selenium-weread-challenge-selenium-oect1 ls -ld /var/tmp')
    result = stdout.read().decode().strip()
    print(result)
    
    client.close()
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
