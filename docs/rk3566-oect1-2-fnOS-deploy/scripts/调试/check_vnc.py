#!/usr/bin/env python3
"""
检查 VNC 服务状态
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
    print("VNC 服务检查")
    print("=" * 60)
    
    # 检查 7900 端口监听
    print("\n【端口监听】")
    stdin, stdout, stderr = client.exec_command('netstat -tlnp | grep 7900')
    result = stdout.read().decode().strip()
    if result:
        print(result)
    else:
        print("7900 端口未监听")
    
    # 检查 Selenium 容器内的 VNC 进程
    print("\n【Selenium 容器内 VNC 进程】")
    stdin, stdout, stderr = client.exec_command('docker exec selenium-weread-challenge-selenium-oect1 ps aux | grep -i vnc')
    result = stdout.read().decode().strip()
    if result:
        print(result)
    else:
        print("未找到 VNC 进程")
    
    # 检查 Selenium 容器日志
    print("\n【Selenium 容器日志（最近20行）】")
    stdin, stdout, stderr = client.exec_command('docker logs selenium-weread-challenge-selenium-oect1 2>&1 | tail -20')
    result = stdout.read().decode().strip()
    print(result)
    
    # 检查环境变量
    print("\n【Selenium 环境变量】")
    stdin, stdout, stderr = client.exec_command('docker exec selenium-weread-challenge-selenium-oect1 env | grep -i vnc')
    result = stdout.read().decode().strip()
    if result:
        print(result)
    else:
        print("未找到 VNC 相关环境变量")
    
    client.close()
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
