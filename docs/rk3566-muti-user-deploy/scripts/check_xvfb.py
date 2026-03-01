#!/usr/bin/env python3
"""
检查 Xvfb 启动问题
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
    print("Xvfb 启动问题诊断")
    print("=" * 60)
    
    # 检查 xvfb 启动脚本
    print("\n【1. Xvfb 启动脚本】")
    stdin, stdout, stderr = client.exec_command('docker exec selenium-weread-challenge-selenium-muti-user cat /opt/bin/start-xvfb.sh 2>/dev/null || echo "文件不存在"')
    result = stdout.read().decode().strip()
    print(result[:600] if len(result) > 600 else result)
    
    # 检查 xvfb 日志
    print("\n【2. Xvfb 相关日志】")
    stdin, stdout, stderr = client.exec_command('docker logs selenium-weread-challenge-selenium-muti-user 2>&1 | grep -i xvfb | head -10')
    result = stdout.read().decode().strip()
    print(result if result else "无 Xvfb 日志")
    
    # 检查 supervisord 管理的进程
    print("\n【3. Supervisord 进程状态】")
    stdin, stdout, stderr = client.exec_command('docker exec selenium-weread-challenge-selenium-muti-user supervisorctl status 2>/dev/null || echo "supervisorctl 不可用"')
    result = stdout.read().decode().strip()
    print(result)
    
    # 检查 SE_START_XVFB 环境变量
    print("\n【4. XVFB 环境变量】")
    stdin, stdout, stderr = client.exec_command('docker exec selenium-weread-challenge-selenium-muti-user env | grep -i xvfb')
    result = stdout.read().decode().strip()
    print(result if result else "未设置")
    
    # 检查所有进程
    print("\n【5. 所有进程】")
    stdin, stdout, stderr = client.exec_command('docker exec selenium-weread-challenge-selenium-muti-user ps aux')
    result = stdout.read().decode().strip()
    print(result)
    
    client.close()
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
