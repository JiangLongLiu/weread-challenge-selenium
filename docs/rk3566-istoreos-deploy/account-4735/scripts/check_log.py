#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查 App 日志"""

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

print("=== App 日志 ===")
stdin, stdout, stderr = client.exec_command("docker logs weread-challenge-selenium-app-1 --tail 15")
print(stdout.read().decode())

client.close()