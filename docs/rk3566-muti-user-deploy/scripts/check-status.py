#!/usr/bin/env python3
"""
4用户状态检查脚本 - 无人值守版本
"""

import pandas as pd
import paramiko

PASSWORD_FILE = r'E:\Qoder_workspace\weread-challenge-selenium\docs\rk3566-muti-user-deploy\password.xls'
REMOTE_DIR = "/mnt/sata1-1/docker/mycontainers/weread-challenge-selenium-muti-user"


def get_credentials():
    df = pd.read_excel(PASSWORD_FILE)
    row = df.iloc[0]
    return {
        'host': str(row['IP地址']).strip(),
        'port': int(row['SSH端口']),
        'username': str(row['用户名']).strip(),
        'password': str(row['密码']).strip()
    }


def create_ssh_client(cred):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(
        hostname=cred['host'],
        port=cred['port'],
        username=cred['username'],
        password=cred['password']
    )
    return client


def check_status():
    print("=" * 60)
    print("4用户状态检查")
    print("=" * 60)
    
    cred = get_credentials()
    print(f"\n主机: {cred['host']}")
    
    ssh = create_ssh_client(cred)
    try:
        # 检查容器
        print("\n【容器状态】")
        stdin, stdout, stderr = ssh.exec_command(f"cd {REMOTE_DIR} && docker compose ps")
        result = stdout.read().decode()
        if result:
            print(result)
        else:
            print("  无运行中的容器")
        
        # 检查定时任务
        print("\n【定时任务】")
        stdin, stdout, stderr = ssh.exec_command("crontab -l | grep weread-multi")
        result = stdout.read().decode()
        if result:
            lines = result.strip().split('\n')
            comment_count = sum(1 for line in lines if line.startswith('#'))
            task_count = sum(1 for line in lines if not line.startswith('#') and line.strip())
            print(f"  注释行: {comment_count} | 任务行: {task_count} | 总计: {len(lines)}")
            for line in lines:
                if line.startswith('#'):
                    print(f"\n{line}")
                else:
                    parts = line.split()
                    if len(parts) >= 5:
                        time_str = f"{parts[0]} {parts[1]} {parts[2]} {parts[3]} {parts[4]}"
                        print(f"  {time_str}")
        else:
            print("  无定时任务")
        
        # 检查数据目录
        print("\n【数据目录】")
        users = ['liujl4735', 'liujl3016', 'jpx155', 'jpx181']
        for user in users:
            stdin, stdout, stderr = ssh.exec_command(f"ls -la {REMOTE_DIR}/data/{user} 2>/dev/null | head -5")
            result = stdout.read().decode()
            if result:
                print(f"  ✓ {user}: 已创建")
            else:
                print(f"  ✗ {user}: 未创建")
        
    finally:
        ssh.close()


if __name__ == "__main__":
    check_status()
