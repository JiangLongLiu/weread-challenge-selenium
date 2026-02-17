#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
account-4735 状态检查脚本

功能：
1. 从 password.xls 读取 SSH 密码
2. 检查容器运行状态
3. 检查定时任务配置

使用：
    python docs/rk3566-istoreos-deploy/account-4735/scripts/check-status.py
"""

import os
import sys
import subprocess
import pandas as pd
import paramiko
from paramiko import SSHClient, AutoAddPolicy

# 配置路径
PASSWORD_FILE = r'E:\Qoder_workspace\weread-challenge-selenium\docs\rk3566-istoreos-deploy\account-4735\password.xls'


def read_password_from_excel(excel_path):
    """从 Excel 文件读取主机密码"""
    try:
        df = pd.read_excel(excel_path)
        row = df.iloc[0]
        return {
            'host': row['IP地址'],
            'username': row['用户名'],
            'password': str(row['密码']),
            'port': int(row['SSH端口']),
            'remark': row['备注']
        }
    except Exception as e:
        print(f"读取密码文件失败: {e}")
        sys.exit(1)


def connect_ssh(host, port, username, password):
    """建立 SSH 连接"""
    client = SSHClient()
    client.set_missing_host_key_policy(AutoAddPolicy())
    try:
        client.connect(hostname=host, port=port, username=username, password=password, timeout=30)
        return client
    except Exception as e:
        print(f"SSH 连接失败: {e}")
        sys.exit(1)


def check_container_status(ssh_client):
    """检查容器运行状态"""
    print("\n" + "=" * 50)
    print("容器状态")
    print("=" * 50)
    stdin, stdout, stderr = ssh_client.exec_command(
        'docker ps --filter "name=weread-challenge-selenium" --format "table {{.Names}}\t{{.Status}}"'
    )
    print(stdout.read().decode())


def check_cron_tasks(ssh_client):
    """检查定时任务"""
    print("\n" + "=" * 50)
    print("定时任务")
    print("=" * 50)
    stdin, stdout, stderr = ssh_client.exec_command('crontab -l')
    result = stdout.read().decode()
    if 'account-4735' in result:
        for line in result.split('\n'):
            if 'account-4735' in line or 'weread-challenge-selenium' in line:
                print(line)
    else:
        print("未找到 account-4735 定时任务")


def main():
    print("=" * 50)
    print("account-4735 状态检查")
    print("=" * 50)

    # 读取密码
    host_info = read_password_from_excel(PASSWORD_FILE)
    print(f"主机: {host_info['host']} ({host_info['remark']})")

    # SSH 连接
    ssh_client = connect_ssh(
        host_info['host'],
        host_info['port'],
        host_info['username'],
        host_info['password']
    )

    try:
        check_container_status(ssh_client)
        check_cron_tasks(ssh_client)
        print("\n" + "=" * 50)
        print("检查完成")
        print("=" * 50)
    finally:
        ssh_client.close()


if __name__ == '__main__':
    main()
