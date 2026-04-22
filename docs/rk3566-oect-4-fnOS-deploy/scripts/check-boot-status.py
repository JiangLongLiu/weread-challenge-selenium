#!/usr/bin/env python3
"""检查主机重启后的启动流程状态"""
import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(hostname='192.168.123.54', port=22, username='root', password='1234567890')

print("=" * 80)
print("主机重启后启动流程检查")
print("=" * 80)

# 1. 检查系统启动时间
print("\n【1. 系统启动时间】")
stdin, stdout, stderr = ssh.exec_command('uptime -s')
boot_time = stdout.read().decode().strip()
print(f"系统启动时间：{boot_time}")

# 2. 检查 systemd 服务状态
print("\n【2. systemd 服务状态】")
stdin, stdout, stderr = ssh.exec_command('systemctl status weread-selenium.service 2>&1 | head -20')
service_status = stdout.read().decode()
print(service_status)

# 3. 检查开机启动脚本
print("\n【3. 开机启动脚本】")
stdin, stdout, stderr = ssh.exec_command('ls -la /etc/systemd/system/weread-selenium.service')
service_file = stdout.read().decode().strip()
print(service_file if service_file else "服务文件不存在")

# 4. 检查 Docker 容器状态
print("\n【4. Docker 容器状态】")
stdin, stdout, stderr = ssh.exec_command('cd /vol1/docker/mycontainers/weread-challenge-selenium-muti-user && docker compose ps')
containers = stdout.read().decode()
print(containers if containers else "无运行中的容器")

# 5. 检查 Selenium 容器详情
print("\n【5. Selenium 容器详情】")
stdin, stdout, stderr = ssh.exec_command('docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep selenium')
selenium_status = stdout.read().decode().strip()
print(selenium_status if selenium_status else "Selenium 容器未运行")

# 6. 检查 VNC 端口
print("\n【6. VNC 端口监听】")
stdin, stdout, stderr = ssh.exec_command('netstat -tlnp | grep 7900')
vnc_port = stdout.read().decode().strip()
print(vnc_port if vnc_port else "7900 端口未监听")

# 7. 检查开机启动日志
print("\n【7. 开机启动日志】")
stdin, stdout, stderr = ssh.exec_command('journalctl -u weread-selenium.service --since boot | tail -30')
boot_log = stdout.read().decode()
print(boot_log)

# 8. 检查 X11 socket（确认是否清理）
print("\n【8. X11 socket 状态】")
stdin, stdout, stderr = ssh.exec_command('ls -la /tmp/.X11-unix/ 2>/dev/null || echo "目录不存在"')
x11_status = stdout.read().decode().strip()
print(x11_status)

# 9. 检查定时任务
print("\n【9. 定时任务状态】")
stdin, stdout, stderr = ssh.exec_command('crontab -l | grep "weread-multi" | head -5')
cron_tasks = stdout.read().decode().strip()
print(cron_tasks if cron_tasks else "无定时任务")

# 10. 检查容器日志（最近 20 行）
print("\n【10. Selenium 容器日志（最近 20 行）】")
stdin, stdout, stderr = ssh.exec_command('docker logs weread-challenge-selenium-muti-user 2>&1 | tail -20')
container_log = stdout.read().decode()
print(container_log)

print("\n" + "=" * 80)
print("检查完成")
print("=" * 80)

ssh.close()
