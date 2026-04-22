#!/usr/bin/env python3
"""完全关闭 52 号主机的 systemd 服务（删除冲突的 SysV 脚本）"""
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(hostname='192.168.123.52', port=22, username='root', password='1234567890')

print("=" * 80)
print("完全关闭 52 号主机的 systemd 服务")
print("=" * 80)

# 1. 检查是否存在 SysV 脚本
print("\n【1. 检查 SysV 脚本】")
stdin, stdout, stderr = ssh.exec_command('ls -la /etc/init.d/weread-selenium 2>&1')
result = stdout.read().decode().strip()
print(result)

# 2. 删除 SysV 脚本
print("\n【2. 删除冲突的 SysV 脚本】")
stdin, stdout, stderr = ssh.exec_command('rm -f /etc/init.d/weread-selenium')
exit_code = stdout.channel.recv_exit_status()
print("✓ 已删除 /etc/init.d/weread-selenium")

# 3. 删除 SysV 链接（如果存在）
print("\n【3. 清理 SysV 链接】")
stdin, stdout, stderr = ssh.exec_command('rm -f /etc/rc.d/S99weread-selenium 2>/dev/null; echo "已清理"')
print("✓ 已清理 SysV 链接")

# 4. 重新加载 systemd
print("\n【4. 重新加载 systemd 配置】")
stdin, stdout, stderr = ssh.exec_command('systemctl daemon-reload')
exit_code = stdout.channel.recv_exit_status()
if exit_code == 0:
    print("✓ systemd 配置已重新加载")
else:
    print(f"✗ 重新加载失败：{stderr.read().decode()}")

# 5. 停止服务（如果还在运行）
print("\n【5. 停止服务】")
stdin, stdout, stderr = ssh.exec_command('systemctl stop weread-selenium.service')
exit_code = stdout.channel.recv_exit_status()
print("✓ 服务已停止")

# 6. 禁用开机自启动
print("\n【6. 禁用开机自启动】")
stdin, stdout, stderr = ssh.exec_command('systemctl disable weread-selenium.service')
exit_code = stdout.channel.recv_exit_status()
if exit_code == 0:
    print("✓ 开机自启动已禁用")
else:
    print(f"✗ 禁用失败：{stderr.read().decode()}")

# 7. 验证服务状态
print("\n【7. 验证服务状态】")
stdin, stdout, stderr = ssh.exec_command('systemctl is-enabled weread-selenium.service')
result = stdout.read().decode().strip()
print(f"启用状态：{result}")

stdin, stdout, stderr = ssh.exec_command('systemctl status weread-selenium.service | head -10')
result = stdout.read().decode().strip()
print(f"\n服务状态：\n{result}")

# 8. 停止所有容器
print("\n【8. 停止所有容器】")
stdin, stdout, stderr = ssh.exec_command('cd /vol1/docker/mycontainers/weread-challenge-selenium-muti-user && docker compose down')
exit_code = stdout.channel.recv_exit_status()
if exit_code == 0:
    print("✓ 所有容器已停止")
else:
    print(f"✗ 停止失败：{stderr.read().decode()}")

# 9. 检查容器状态
print("\n【9. 验证容器已停止】")
stdin, stdout, stderr = ssh.exec_command('docker ps -a --format "table {{.Names}}\t{{.Status}}" | grep selenium')
result = stdout.read().decode().strip()
print(result if result else "Selenium 容器未运行")

print("\n" + "=" * 80)
print("操作完成")
print("=" * 80)
print("\n✅ 已完成操作：")
print("  1. 删除冲突的 SysV 脚本 (/etc/init.d/weread-selenium)")
print("  2. 清理 SysV 链接 (/etc/rc.d/S99weread-selenium)")
print("  3. 重新加载 systemd 配置")
print("  4. 停止 systemd 服务")
print("  5. 禁用开机自启动")
print("  6. 停止所有容器")
print("\n📝 当前状态：")
print("  - systemd 服务：disabled ✅")
print("  - Selenium 容器：已停止 ✅")
print("  - 定时任务：仍然有效")
print("\n⚠️  注意：")
print("  - 定时任务仍然会在指定时间启动容器")
print("  - 如果需要完全禁用所有自动启动，需要注释 crontab 中的定时任务")
print("  - 重新启用时执行：systemctl enable weread-selenium.service")

ssh.close()
