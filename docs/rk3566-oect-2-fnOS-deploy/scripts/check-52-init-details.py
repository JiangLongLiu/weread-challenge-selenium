#!/usr/bin/env python3
"""详细检查 52 号主机的启动配置"""
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(hostname='192.168.123.52', port=22, username='root', password='1234567890')

print("=" * 80)
print("详细检查 52 号主机启动配置")
print("=" * 80)

# 1. 检查 /etc/init.d/weread-selenium 内容
print("\n【1. /etc/init.d/weread-selenium 内容】")
stdin, stdout, stderr = ssh.exec_command('cat /etc/init.d/weread-selenium')
result = stdout.read().decode().strip()
print(result if result else "文件不存在")

# 2. 检查 /etc/rc.d/ 下的链接
print("\n【2. /etc/rc.d/ 下的链接】")
stdin, stdout, stderr = ssh.exec_command('ls -la /etc/rc.d/ | grep weread')
result = stdout.read().decode().strip()
print(result if result else "无链接")

# 3. 检查 systemd 是否使用 SysV 兼容
print("\n【3. systemd 与 SysV 的关系】")
stdin, stdout, stderr = ssh.exec_command('systemctl status weread-selenium.service | grep -E "Loaded|SysV"')
result = stdout.read().decode().strip()
print(result)

# 4. 检查服务启用状态的详细信息
print("\n【4. systemctl is-enabled 详细输出】")
stdin, stdout, stderr = ssh.exec_command('systemctl is-enabled weread-selenium.service && echo "---" && ls -la /etc/systemd/system/multi-user.target.wants/ | grep weread')
result = stdout.read().decode().strip()
print(result)

# 5. 检查 /etc/init.d 中是否有其他 weread 相关脚本
print("\n【5. /etc/init.d 中的 weread 相关脚本】")
stdin, stdout, stderr = ssh.exec_command('ls -la /etc/init.d/ | grep weread')
result = stdout.read().decode().strip()
print(result if result else "无 weread 相关脚本")

# 6. 检查 update-rc.d 状态
print("\n【6. update-rc.d 状态】")
stdin, stdout, stderr = ssh.exec_command('update-rc.d -n weread-selenium show 2>&1 || echo "命令不可用"')
result = stdout.read().decode().strip()
print(result)

print("\n" + "=" * 80)
print("检查完成")
print("=" * 80)

ssh.close()
