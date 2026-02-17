#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查 DNS 问题"""

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

print("=== 测试 DNS 解析 (容器内) ===")
stdin, stdout, stderr = client.exec_command("docker exec weread-challenge-selenium-selenium-1 curl -sI https://weread.qq.com --connect-timeout 15 2>&1 | head -5 || echo 'curl failed'")
print(stdout.read().decode())

print("=== 测试 IP 直连 ===")
stdin, stdout, stderr = client.exec_command("docker exec weread-challenge-selenium-selenium-1 curl -sI https://43.159.233.235 --connect-timeout 10 -k 2>&1 | head -3 || echo 'curl failed'")
print(stdout.read().decode())

print("=== 测试 DNS 解析 (宿主机) ===")
stdin, stdout, stderr = client.exec_command("ping -c 2 weread.qq.com 2>&1 || echo 'ping failed'")
print(stdout.read().decode())

print("=== App 日志 ===")
stdin, stdout, stderr = client.exec_command("docker logs weread-challenge-selenium-app-1 --tail 15")
print(stdout.read().decode())

client.close()