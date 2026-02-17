#!/usr/bin/env python3
"""
4用户远程部署脚本 - 无人值守版本
自动从 password.xls 读取 SSH 凭据
"""

import pandas as pd
import paramiko
from scp import SCPClient
import os

# 配置
PASSWORD_FILE = r'E:\Qoder_workspace\weread-challenge-selenium\docs\rk3566-muti-user-deploy\password.xls'
LOCAL_DIR = r'E:\Qoder_workspace\weread-challenge-selenium\docs\rk3566-muti-user-deploy'
REMOTE_DIR = "/mnt/sata1-1/docker/mycontainers/weread-challenge-selenium-muti-user"


def get_credentials():
    """从 Excel 读取 SSH 凭据"""
    df = pd.read_excel(PASSWORD_FILE)
    row = df.iloc[0]
    return {
        'host': str(row['IP地址']).strip(),
        'port': int(row['SSH端口']),
        'username': str(row['用户名']).strip(),
        'password': str(row['密码']).strip()
    }


def create_ssh_client(cred):
    """创建 SSH 连接"""
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(
        hostname=cred['host'],
        port=cred['port'],
        username=cred['username'],
        password=cred['password']
    )
    return client


def deploy():
    """执行部署"""
    print("=" * 60)
    print("RK3566 4用户微信读书助手部署")
    print("=" * 60)
    
    # 读取凭据
    print("\n[1/6] 读取 SSH 凭据...")
    cred = get_credentials()
    print(f"  主机: {cred['host']}:{cred['port']}")
    print(f"  用户: {cred['username']}")
    
    # 连接 SSH
    print("\n[2/6] 连接远程主机...")
    ssh = create_ssh_client(cred)
    print("  连接成功")
    
    try:
        # 创建远程目录
        print("\n[3/6] 创建远程工作目录...")
        ssh.exec_command(f"mkdir -p {REMOTE_DIR}")
        
        # 上传文件
        print("\n[4/6] 上传部署文件...")
        with SCPClient(ssh.get_transport()) as scp:
            scp.put(f"{LOCAL_DIR}/docker-compose.yml", f"{REMOTE_DIR}/docker-compose.yml")
            print("  ✓ docker-compose.yml")
        
        # 创建用户数据目录
        print("\n[5/6] 创建用户数据目录...")
        users = ['liujl4735', 'liujl3016', 'jpx155', 'jpx181']
        for user in users:
            ssh.exec_command(f"mkdir -p {REMOTE_DIR}/data/{user}")
            print(f"  ✓ {user}")
        
        # 配置定时任务
        print("\n[6/6] 配置定时任务...")
        setup_cron(ssh)
        
        print("\n" + "=" * 60)
        print("部署完成!")
        print("=" * 60)
        print(f"\n工作目录: {REMOTE_DIR}")
        print(f"VNC 地址: http://{cred['host']}:7900")
        print(f"\n用户时间表:")
        print("  liujl4735: 00:00, 06:00, 13:00, 19:00")
        print("  liujl3016: 01:10, 07:10, 14:10, 20:10")
        print("  jpx155:    02:20, 08:20, 15:20, 21:20")
        print("  jpx181:    03:30, 09:30, 16:30, 22:30")
        
    finally:
        ssh.close()


def setup_cron(ssh):
    """配置定时任务"""
    # 清理旧任务
    ssh.exec_command("crontab -l 2>/dev/null | grep -v 'weread-multi' | crontab -")
    
    # 添加新任务
    cron_cmds = [
        # liujl4735
        "(crontab -l 2>/dev/null; echo '# weread-multi: liujl4735') | crontab -",
        f"(crontab -l 2>/dev/null; echo '0 0 * * * cd {REMOTE_DIR} && docker compose up app-1 -d') | crontab -",
        f"(crontab -l 2>/dev/null; echo '0 6 * * * cd {REMOTE_DIR} && docker compose up app-1 -d') | crontab -",
        f"(crontab -l 2>/dev/null; echo '0 13 * * * cd {REMOTE_DIR} && docker compose up app-1 -d') | crontab -",
        f"(crontab -l 2>/dev/null; echo '0 19 * * * cd {REMOTE_DIR} && docker compose up app-1 -d') | crontab -",
        # liujl3016
        "(crontab -l 2>/dev/null; echo '# weread-multi: liujl3016') | crontab -",
        f"(crontab -l 2>/dev/null; echo '10 1 * * * cd {REMOTE_DIR} && docker compose up app-2 -d') | crontab -",
        f"(crontab -l 2>/dev/null; echo '10 7 * * * cd {REMOTE_DIR} && docker compose up app-2 -d') | crontab -",
        f"(crontab -l 2>/dev/null; echo '10 14 * * * cd {REMOTE_DIR} && docker compose up app-2 -d') | crontab -",
        f"(crontab -l 2>/dev/null; echo '10 20 * * * cd {REMOTE_DIR} && docker compose up app-2 -d') | crontab -",
        # jpx155
        "(crontab -l 2>/dev/null; echo '# weread-multi: jpx155') | crontab -",
        f"(crontab -l 2>/dev/null; echo '20 2 * * * cd {REMOTE_DIR} && docker compose up app-3 -d') | crontab -",
        f"(crontab -l 2>/dev/null; echo '20 8 * * * cd {REMOTE_DIR} && docker compose up app-3 -d') | crontab -",
        f"(crontab -l 2>/dev/null; echo '20 15 * * * cd {REMOTE_DIR} && docker compose up app-3 -d') | crontab -",
        f"(crontab -l 2>/dev/null; echo '20 21 * * * cd {REMOTE_DIR} && docker compose up app-3 -d') | crontab -",
        # jpx181
        "(crontab -l 2>/dev/null; echo '# weread-multi: jpx181') | crontab -",
        f"(crontab -l 2>/dev/null; echo '30 3 * * * cd {REMOTE_DIR} && docker compose up app-4 -d') | crontab -",
        f"(crontab -l 2>/dev/null; echo '30 9 * * * cd {REMOTE_DIR} && docker compose up app-4 -d') | crontab -",
        f"(crontab -l 2>/dev/null; echo '30 16 * * * cd {REMOTE_DIR} && docker compose up app-4 -d') | crontab -",
        f"(crontab -l 2>/dev/null; echo '30 22 * * * cd {REMOTE_DIR} && docker compose up app-4 -d') | crontab -",
    ]
    
    for cmd in cron_cmds:
        ssh.exec_command(cmd)
    
    print("  ✓ 16个定时任务已配置")


if __name__ == "__main__":
    deploy()
