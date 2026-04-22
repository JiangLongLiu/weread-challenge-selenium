#!/usr/bin/env python3
"""诊断开机启动失败原因"""
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(hostname='192.168.123.54', port=22, username='root', password='1234567890')

print("=" * 80)
print("开机启动故障诊断")
print("=" * 80)

# 1. 检查 /etc/init.d/weread-selenium 是否存在
print("\n【1. 检查 /etc/init.d/weread-selenium】")
stdin, stdout, stderr = ssh.exec_command('ls -la /etc/init.d/weread-selenium 2>&1')
result = stdout.read().decode().strip()
print(result if result else "文件不存在")

# 2. 检查 /etc/rc.d/S99weread-selenium 链接
print("\n【2. 检查 /etc/rc.d/S99weread-selenium】")
stdin, stdout, stderr = ssh.exec_command('ls -la /etc/rc.d/S99weread-selenium 2>&1')
result = stdout.read().decode().strip()
print(result if result else "链接不存在")

# 3. 检查 systemd 服务文件
print("\n【3. 检查 systemd 服务文件】")
stdin, stdout, stderr = ssh.exec_command('ls -la /etc/systemd/system/weread-selenium.service 2>&1')
result = stdout.read().decode().strip()
print(result if result else "文件不存在")

# 4. 检查 systemd 服务是否启用
print("\n【4. 检查 systemd 服务启用状态】")
stdin, stdout, stderr = ssh.exec_command('systemctl is-enabled weread-selenium.service 2>&1')
result = stdout.read().decode().strip()
print(f"服务状态：{result if result else '未知'}")

# 5. 查看所有 weread 相关的 systemd 服务
print("\n【5. 查看所有 weread 相关的 systemd 服务】")
stdin, stdout, stderr = ssh.exec_command('systemctl list-unit-files | grep weread')
result = stdout.read().decode().strip()
print(result if result else "无 weread 相关服务")

# 6. 检查启动脚本内容
print("\n【6. 检查 /etc/init.d/weread-selenium 内容】")
stdin, stdout, stderr = ssh.exec_command('cat /etc/init.d/weread-selenium 2>&1')
result = stdout.read().decode().strip()
print(result if result else "文件不存在或为空")

# 7. 检查系统日志中 weread 相关条目
print("\n【7. 系统日志中 weread 相关条目】")
stdin, stdout, stderr = ssh.exec_command('journalctl -xb | grep -i weread | tail -20')
result = stdout.read().decode().strip()
print(result if result else "无相关日志")

# 8. 检查 Docker 服务状态
print("\n【8. Docker 服务状态】")
stdin, stdout, stderr = ssh.exec_command('systemctl status docker | head -10')
result = stdout.read().decode().strip()
print(result)

# 9. 手动测试启动脚本
print("\n【9. 手动测试启动脚本】")
stdin, stdout, stderr = ssh.exec_command('/etc/init.d/weread-selenium status 2>&1')
result = stdout.read().decode().strip()
print(result)

print("\n" + "=" * 80)
print("诊断完成")
print("=" * 80)

ssh.close()
