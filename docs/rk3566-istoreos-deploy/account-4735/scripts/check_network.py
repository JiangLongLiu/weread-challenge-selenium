#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查 RK3566 上的网络连接问题
"""

import pandas as pd
import paramiko

# 读取密码
PASSWORD_FILE = r'E:\Qoder_workspace\weread-challenge-selenium\docs\rk3566-istoreos-deploy\account-4735\password.xls'
df = pd.read_excel(PASSWORD_FILE)
row = df.iloc[0]
host = row['IP地址']
username = row['用户名']
password = str(row['密码'])
port = int(row['SSH端口'])

print(f"连接到 {host}:{port}...")

# SSH 连接
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, port, username, password, timeout=30)

print("SSH 连接成功!\n")

# 检查容器网络
commands = [
    # 检查容器能否访问外网
    ("测试网络连接", "docker exec weread-challenge-selenium-selenium-1 curl -sI https://weread.qq.com --connect-timeout 15 2>&1 | head -5 || echo 'curl failed'"),
    ("检查容器 DNS 配置", "docker exec weread-challenge-selenium-selenium-1 cat /etc/resolv.conf"),
    ("检查代理环境变量", "docker exec weread-challenge-selenium-selenium-1 env | grep -i proxy"),
    ("检查 App 日志", "docker logs weread-challenge-selenium-app-1 --tail 20"),
]

for title, cmd in commands:
    print(f"=== {title} ===")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
    print(stdout.read().decode())
    err = stderr.read().decode()
    if err:
        print("STDERR:", err)
    print()

client.close()
print("检查完成")