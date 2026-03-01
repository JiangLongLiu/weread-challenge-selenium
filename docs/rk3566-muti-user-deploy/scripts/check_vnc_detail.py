#!/usr/bin/env python3
"""
详细检查 VNC 问题
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
    print("VNC 详细诊断")
    print("=" * 60)
    
    # 检查 VNC 启动脚本
    print("\n【1. VNC 启动脚本】")
    stdin, stdout, stderr = client.exec_command('docker exec weread-challenge-selenium-muti-user-selenium-1 cat /opt/bin/start-vnc.sh 2>/dev/null || echo "文件不存在"')
    result = stdout.read().decode().strip()
    print(result[:800] if len(result) > 800 else result)
    
    # 检查 VNC 相关日志
    print("\n【2. VNC 启动日志】")
    stdin, stdout, stderr = client.exec_command('docker logs weread-challenge-selenium-muti-user-selenium-1 2>&1 | grep -i vnc | head -20')
    result = stdout.read().decode().strip()
    print(result if result else "无 VNC 日志")
    
    # 检查 5900 相关日志
    print("\n【3. 5900 端口日志】")
    stdin, stdout, stderr = client.exec_command('docker logs weread-challenge-selenium-muti-user-selenium-1 2>&1 | grep 5900 | head -10')
    result = stdout.read().decode().strip()
    print(result if result else "无 5900 相关日志")
    
    # 检查显示服务器
    print("\n【4. 显示服务器进程】")
    stdin, stdout, stderr = client.exec_command('docker exec weread-challenge-selenium-muti-user-selenium-1 ps aux | grep -E "Xvfb|display" | grep -v grep')
    result = stdout.read().decode().strip()
    print(result if result else "无显示服务器进程")
    
    # 检查 DISPLAY 环境变量
    print("\n【5. DISPLAY 环境变量】")
    stdin, stdout, stderr = client.exec_command('docker exec weread-challenge-selenium-muti-user-selenium-1 env | grep DISPLAY')
    result = stdout.read().decode().strip()
    print(result if result else "DISPLAY 未设置")
    
    # 检查所有监听端口
    print("\n【6. 所有监听端口】")
    stdin, stdout, stderr = client.exec_command('docker exec weread-challenge-selenium-muti-user-selenium-1 netstat -tlnp 2>/dev/null || echo "netstat 不可用"')
    result = stdout.read().decode().strip()
    print(result)
    
    client.close()
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
