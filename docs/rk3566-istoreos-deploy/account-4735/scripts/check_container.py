#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查容器 DNS 配置"""

import pandas as pd
import paramiko

PASSWORD_FILE = r'E:\Qoder_workspace\weread-challenge-selenium\docs\rk3566-istoreos-deploy\account-4735\password.xls'
df = pd.read_excel(PASSWORD_FILE)
row = df.iloc[0]
host = row['IP地址']
username = row['用户名']
password = str(row['密码'])
port = int(row['SSH端口'])

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, port, username, password, timeout=30)

print("=== 容器 DNS 配置 ===")
stdin, stdout, stderr = client.exec_command("docker exec weread-challenge-selenium-selenium-1 cat /etc/resolv.conf")
print(stdout.read().decode())

print("=== 宿主机 DNS 配置 ===")
stdin, stdout, stderr = client.exec_command("cat /etc/resolv.conf")
print(stdout.read().decode())

print("=== 测试 curl 访问微信读书 ===")
stdin, stdout, stderr = client.exec_command("docker exec weread-challenge-selenium-selenium-1 curl -sI https://weread.qq.com --connect-timeout 10 2>&1 | head -10")
print(stdout.read().decode())

print("=== App 日志 ===")
stdin, stdout, stderr = client.exec_command("docker logs weread-challenge-selenium-app-1 --tail 10")
print(stdout.read().decode())

client.close()