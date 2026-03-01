#!/usr/bin/env python3
"""
测试 Xvfb 启动
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
    print("Xvfb 启动测试")
    print("=" * 60)
    
    # 检查 supervisord 配置
    print("\n【1. Supervisord Xvfb 配置】")
    stdin, stdout, stderr = client.exec_command('docker exec selenium-weread-challenge-selenium-muti-user cat /etc/supervisor/conf.d/selenium.conf 2>/dev/null | grep -A10 xvfb')
    result = stdout.read().decode().strip()
    print(result if result else "配置未找到")
    
    # 检查环境变量传递
    print("\n【2. 环境变量检查】")
    stdin, stdout, stderr = client.exec_command('docker exec selenium-weread-challenge-selenium-muti-user env | grep -E "SE_SCREEN|SE_START_XVFB"')
    result = stdout.read().decode().strip()
    print(result if result else "环境变量未设置")
    
    # 检查 start-xvfb.sh 完整内容
    print("\n【3. start-xvfb.sh 完整内容】")
    stdin, stdout, stderr = client.exec_command('docker exec selenium-weread-challenge-selenium-muti-user cat /opt/bin/start-xvfb.sh')
    result = stdout.read().decode().strip()
    print(result)
    
    client.close()
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
