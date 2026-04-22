#!/usr/bin/env python3
"""主机重启后完整状态检查"""
import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(hostname='192.168.123.54', port=22, username='root', password='1234567890')

print("=" * 80)
print("主机重启后启动流程检查报告")
print("=" * 80)
print(f"检查时间：{time.strftime('%Y-%m-%d %H:%M:%S')}")

# 1. 系统启动时间
print("\n【1. 系统信息】")
stdin, stdout, stderr = ssh.exec_command('uptime -s')
boot_time = stdout.read().decode().strip()
print(f"系统启动时间：{boot_time}")

# 2. systemd 服务状态
print("\n【2. systemd 服务状态】")
stdin, stdout, stderr = ssh.exec_command('systemctl status weread-selenium.service | grep -E "Loaded|Active"')
service_status = stdout.read().decode().strip()
print(service_status)

# 3. Docker 容器状态
print("\n【3. Docker 容器状态】")
stdin, stdout, stderr = ssh.exec_command('cd /vol1/docker/mycontainers/weread-challenge-selenium-muti-user && docker compose ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"')
containers = stdout.read().decode().strip()
print(containers)

# 4. VNC 端口检查
print("\n【4. VNC 端口检查】")
stdin, stdout, stderr = ssh.exec_command('docker exec weread-challenge-selenium-muti-user netstat -tlnp 2>/dev/null | grep -E "7900|5900"')
vnc_port = stdout.read().decode().strip()
print(f"VNC 端口监听：{vnc_port if vnc_port else '容器内端口未监听'}")

# 5. 容器日志（最后 10 行）
print("\n【5. Selenium 容器日志（最后 10 行）")
stdin, stdout, stderr = ssh.exec_command('docker logs weread-challenge-selenium-muti-user 2>&1 | tail -10')
logs = stdout.read().decode().strip()
print(logs)

# 6. 定时任务
print("\n【6. 定时任务状态】")
stdin, stdout, stderr = ssh.exec_command('crontab -l | grep -E "weread-multi|daily cleanup" | wc -l')
cron_count = stdout.read().decode().strip()
print(f"定时任务数量：{cron_count}")

# 7. 数据目录
print("\n【7. 数据目录】")
stdin, stdout, stderr = ssh.exec_command('ls -la /vol1/docker/mycontainers/weread-challenge-selenium-muti-user/data/ | grep "^d" | wc -l')
dir_count = stdout.read().decode().strip()
print(f"用户数据目录数量：{dir_count}")

# 8. 开机启动脚本
print("\n【8. 开机启动脚本】")
stdin, stdout, stderr = ssh.exec_command('ls -la /etc/systemd/system/weread-selenium.service')
service_file = stdout.read().decode().strip()
print(f"systemd 服务文件：{service_file if service_file else '不存在'}")

# 9. 服务启用状态
print("\n【9. 服务启用状态】")
stdin, stdout, stderr = ssh.exec_command('systemctl is-enabled weread-selenium.service')
enabled_status = stdout.read().decode().strip()
print(f"服务启用状态：{enabled_status}")

print("\n" + "=" * 80)
print("检查结论")
print("=" * 80)

# 综合判断
issues = []
if "disabled" in enabled_status:
    issues.append("⚠ 服务未启用开机自启动")
if not containers:
    issues.append("⚠ Selenium 容器未运行")
if not vnc_port:
    issues.append("⚠ VNC 端口未监听（可能需要访问 VNC 触发）")

if issues:
    print("\n发现的问题：")
    for issue in issues:
        print(f"  {issue}")
else:
    print("\n✅ 所有检查项正常！")

print("\n建议操作：")
print("  1. 访问 VNC: http://192.168.123.54:7900 (密码：111111)")
print("  2. 等待下一个时间窗口观察自动启动")
print("  3. 查看日志：docker compose logs -f app-1")

print("\n" + "=" * 80)

ssh.close()
