#!/usr/bin/env python3
"""
检查 Xvfb 错误日志
"""

import pandas as pd
import paramiko

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
    
    print("=" * 60)
    print("Xvfb 错误诊断")
    print("=" * 60)
    
    # 检查 Xvfb 的详细日志
    print("\n【1. Xvfb 退出日志】")
    stdin, stdout, stderr = client.exec_command('docker logs weread-challenge-selenium-muti-user 2>&1 | grep -E "(exited: xvfb|xvfb exited)"')
    result = stdout.read().decode().strip()
    print(result if result else "无退出日志")
    
    # 检查 Xvfb 启动前的日志
    print("\n【2. Xvfb 启动日志】")
    stdin, stdout, stderr = client.exec_command('docker logs weread-challenge-selenium-muti-user 2>&1 | grep -E "(spawned: xvfb|success: xvfb)"')
    result = stdout.read().decode().strip()
    print(result if result else "无启动日志")
    
    # 检查是否有错误信息
    print("\n【3. Xvfb 错误信息】")
    stdin, stdout, stderr = client.exec_command('docker logs weread-challenge-selenium-muti-user 2>&1 | grep -iE "(error|fail|cannot|unable)" | grep -i xvfb')
    result = stdout.read().decode().strip()
    print(result if result else "无错误信息")
    
    # 检查 Xvfb 是否安装
    print("\n【4. Xvfb 安装检查】")
    stdin, stdout, stderr = client.exec_command('docker exec weread-challenge-selenium-muti-user which Xvfb')
    result = stdout.read().decode().strip()
    print(result if result else "Xvfb 未找到")
    
    # 检查 xvfb-run 是否可用
    print("\n【5. xvfb-run 检查】")
    stdin, stdout, stderr = client.exec_command('docker exec weread-challenge-selenium-muti-user which xvfb-run')
    result = stdout.read().decode().strip()
    print(result if result else "xvfb-run 未找到")
    
    # 检查 /tmp 权限
    print("\n【6. /tmp 权限检查】")
    stdin, stdout, stderr = client.exec_command('docker exec weread-challenge-selenium-muti-user ls -ld /tmp')
    result = stdout.read().decode().strip()
    print(result)
    
    client.close()
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
