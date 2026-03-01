#!/usr/bin/env python3
"""
检查 RK3566 时间和定时任务状态
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
    print("RK3566 时间和定时任务检查")
    print("=" * 60)
    
    # 检查系统时间
    print("\n【系统时间】")
    stdin, stdout, stderr = client.exec_command('date "+%Y-%m-%d %H:%M:%S %Z"')
    print(f"RK3566 时间: {stdout.read().decode().strip()}")
    
    # 检查 crond 是否运行
    print("\n【crond 服务】")
    stdin, stdout, stderr = client.exec_command('pgrep crond | wc -l')
    crond_count = stdout.read().decode().strip()
    print(f"crond 进程数: {crond_count}")
    
    # 检查 liujl4735 的 19:00 任务
    print("\n【liujl4735 19:00 任务】")
    stdin, stdout, stderr = client.exec_command('crontab -l 2>/dev/null | grep "0 19" | head -1')
    task_19 = stdout.read().decode().strip()
    if task_19:
        print(f"找到任务: {task_19[:80]}...")
    else:
        print("未找到 19:00 任务")
    
    # 检查当前运行的容器
    print("\n【运行中的容器】")
    stdin, stdout, stderr = client.exec_command('docker ps --format "{{.Names}}|{{.Status}}" | grep weread')
    containers = stdout.read().decode().strip()
    if containers:
        for line in containers.split('\n'):
            if line:
                parts = line.split('|')
                print(f"  - {parts[0]}: {parts[1]}")
    else:
        print("  无运行中的容器")
    
    # 检查最近 2 小时的 cron 日志（如果有）
    print("\n【最近日志】")
    stdin, stdout, stderr = client.exec_command('logread | grep -i "cron\|weread" | tail -5')
    logs = stdout.read().decode().strip()
    if logs:
        print(logs)
    else:
        print("  无相关日志")
    
    client.close()
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
