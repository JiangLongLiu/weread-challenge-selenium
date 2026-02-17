#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试 DNS 速度并选择最优"""

import pandas as pd
import paramiko
import re

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

# 待测试的 DNS 服务器列表
dns_servers = [
    # 国内推荐
    ("114 DNS", "114.114.114.114"),
    ("阿里 DNS", "223.5.5.5"),
    ("阿里 DNS 备用", "223.6.6.6"),
    ("腾讯 DNS", "119.29.29.29"),
    ("腾讯 DNS 备用", "119.28.28.28"),
    ("百度 DNS", "180.76.76.76"),
    ("CNNIC SDNS", "1.2.4.8"),
    ("oneDNS", "117.50.11.11"),
    ("DNS派", "101.226.4.6"),
    # 境外
    ("Cloudflare", "1.1.1.1"),
    ("Google", "8.8.8.8"),
]

print("=" * 60)
print("DNS 速度测试（ping 延迟）")
print("=" * 60)
print(f"{'DNS 名称':<20} {'IP 地址':<18} {'延迟(ms)':<10} {'状态'}")
print("-" * 60)

results = []
for name, dns_ip in dns_servers:
    # ping DNS 服务器测试延迟
    stdin, stdout, stderr = client.exec_command(f"ping -c 3 -W 2 {dns_ip} 2>&1 | tail -1", timeout=15)
    output = stdout.read().decode().strip()
    
    # 解析 ping 结果
    if 'rtt' in output or 'avg' in output:
        try:
            match = re.search(r'= ([\d.]+)/([\d.]+)/([\d.]+)', output)
            if match:
                avg_ms = float(match.group(2))
                status = "OK"
                results.append((name, dns_ip, avg_ms))
            else:
                avg_ms = 999
                status = "FAIL"
        except:
            avg_ms = 999
            status = "FAIL"
    elif '100% packet loss' in output or '0 packets received' in output:
        avg_ms = 999
        status = "FAIL"
    else:
        avg_ms = 999
        status = "FAIL"
    
    print(f"{name:<20} {dns_ip:<18} {avg_ms:<10.1f} {status}")

print("-" * 60)

# 排序并显示最优
results.sort(key=lambda x: x[2])
print("\n推荐 DNS（按延迟排序）：")
print("-" * 60)
for i, (name, dns_ip, ms) in enumerate(results[:5]):
    print(f"{i+1}. {name}: {dns_ip} ({ms:.1f}ms)")

# 推荐前3个
recommended = [r[1] for r in results[:3]]
print(f"\n推荐配置：{recommended}")

client.close()