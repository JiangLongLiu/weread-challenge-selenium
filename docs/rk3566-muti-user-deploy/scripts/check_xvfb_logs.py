#!/usr/bin/env python3
"""
检查 Xvfb 日志文件
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
    print("Xvfb 日志文件检查")
    print("=" * 60)
    
    # 检查 xvfb stderr 日志
    print("\n【1. Xvfb stderr 日志】")
    stdin, stdout, stderr = client.exec_command('docker exec weread-challenge-selenium-muti-user-selenium-1 cat /var/log/supervisor/xvfb-stderr.log 2>/dev/null || echo "日志文件不存在"')
    result = stdout.read().decode().strip()
    print(result if result else "空日志")
    
    # 检查 xvfb stdout 日志
    print("\n【2. Xvfb stdout 日志】")
    stdin, stdout, stderr = client.exec_command('docker exec weread-challenge-selenium-muti-user-selenium-1 cat /var/log/supervisor/xvfb-stdout.log 2>/dev/null || echo "日志文件不存在"')
    result = stdout.read().decode().strip()
    print(result if result else "空日志")
    
    # 检查 vnc 日志
    print("\n【3. VNC stderr 日志】")
    stdin, stdout, stderr = client.exec_command('docker exec weread-challenge-selenium-muti-user-selenium-1 cat /var/log/supervisor/vnc-stderr.log 2>/dev/null || echo "日志文件不存在"')
    result = stdout.read().decode().strip()
    print(result if result else "空日志")
    
    client.close()
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
