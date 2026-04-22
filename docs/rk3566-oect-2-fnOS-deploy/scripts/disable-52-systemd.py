#!/usr/bin/env python3
"""暂时关闭 52 号主机的 systemd 服务"""
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(hostname='192.168.123.52', port=22, username='root', password='1234567890')

print("=" * 80)
print("暂时关闭 52 号主机的 systemd 服务")
print("=" * 80)

# 1. 检查当前服务状态
print("\n【1. 检查当前服务状态】")
stdin, stdout, stderr = ssh.exec_command('systemctl status weread-selenium.service | head -10')
result = stdout.read().decode().strip()
print(result)

# 2. 停止 systemd 服务
print("\n【2. 停止 systemd 服务】")
stdin, stdout, stderr = ssh.exec_command('systemctl stop weread-selenium.service')
exit_code = stdout.channel.recv_exit_status()
if exit_code == 0:
    print("✓ 服务已停止")
else:
    print(f"✗ 停止失败：{stderr.read().decode()}")

# 3. 禁用开机自启动
print("\n【3. 禁用开机自启动】")
stdin, stdout, stderr = ssh.exec_command('systemctl disable weread-selenium.service')
exit_code = stdout.channel.recv_exit_status()
if exit_code == 0:
    print("✓ 开机自启动已禁用")
else:
    print(f"✗ 禁用失败：{stderr.read().decode()}")

# 4. 验证服务状态
print("\n【4. 验证服务状态】")
stdin, stdout, stderr = ssh.exec_command('systemctl is-enabled weread-selenium.service')
result = stdout.read().decode().strip()
print(f"启用状态：{result}")

stdin, stdout, stderr = ssh.exec_command('systemctl status weread-selenium.service | head -10')
result = stdout.read().decode().strip()
print(f"\n服务状态：\n{result}")

# 5. 检查容器状态
print("\n【5. 检查容器状态】")
stdin, stdout, stderr = ssh.exec_command('cd /vol1/docker/mycontainers/weread-challenge-selenium-muti-user && docker compose ps')
result = stdout.read().decode().strip()
print(result if result else "无运行中的容器")

# 6. 停止 Selenium 容器
print("\n【6. 停止 Selenium 容器】")
stdin, stdout, stderr = ssh.exec_command('cd /vol1/docker/mycontainers/weread-challenge-selenium-muti-user && docker compose stop selenium')
exit_code = stdout.channel.recv_exit_status()
if exit_code == 0:
    print("✓ Selenium 容器已停止")
else:
    print(f"✗ 停止失败：{stderr.read().decode()}")

# 7. 再次检查容器状态
print("\n【7. 验证容器已停止】")
stdin, stdout, stderr = ssh.exec_command('docker ps -a --format "table {{.Names}}\t{{.Status}}" | grep selenium')
result = stdout.read().decode().strip()
print(result if result else "Selenium 容器未运行")

print("\n" + "=" * 80)
print("操作完成")
print("=" * 80)
print("\n✅ 已完成操作：")
print("  1. 停止 systemd 服务")
print("  2. 禁用开机自启动")
print("  3. 停止 Selenium 容器")
print("\n📝 当前状态：")
print("  - systemd 服务：disabled")
print("  - Selenium 容器：已停止")
print("  - 定时任务：仍然有效")
print("\n⚠️  注意：")
print("  - 定时任务仍然会在指定时间启动容器")
print("  - 如果需要完全禁用，请注释掉 crontab 中的定时任务")
print("  - 重新启用时执行：systemctl enable weread-selenium.service")

ssh.close()
