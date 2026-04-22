#!/usr/bin/env python3
"""修复 54 号主机 systemd 服务（参考 52 号主机配置）"""
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(hostname='192.168.123.54', port=22, username='root', password='1234567890')

print("=" * 80)
print("修复 54 号主机 systemd 服务（参考 52 号主机）")
print("=" * 80)

# 1. 删除冲突的 SysV 脚本
print("\n【1. 删除 /etc/init.d/weread-selenium】")
stdin, stdout, stderr = ssh.exec_command('rm -f /etc/init.d/weread-selenium')
exit_code = stdout.channel.recv_exit_status()
print("✓ 已删除冲突的 SysV 脚本")
print("  说明：fnOS 使用 Debian systemd，不需要 OpenWrt 格式的 SysV 脚本")

# 2. 删除 SysV 链接（如果存在）
print("\n【2. 清理 SysV 链接】")
stdin, stdout, stderr = ssh.exec_command('rm -f /etc/rc.d/S99weread-selenium 2>/dev/null; echo "已清理"')
print("✓ 已清理 SysV 链接")

# 3. 重新加载 systemd
print("\n【3. 重新加载 systemd 配置】")
stdin, stdout, stderr = ssh.exec_command('systemctl daemon-reload')
exit_code = stdout.channel.recv_exit_status()
if exit_code == 0:
    print("✓ systemd 配置已重新加载")
else:
    print(f"✗ 重新加载失败：{stderr.read().decode()}")

# 4. 启用 systemd 服务（关键步骤）
print("\n【4. 启用 systemd 服务】")
stdin, stdout, stderr = ssh.exec_command('systemctl enable weread-selenium.service')
exit_code = stdout.channel.recv_exit_status()
if exit_code == 0:
    print("✓ 开机自启动已启用 (enabled)")
else:
    print(f"✗ 启用失败：{stderr.read().decode()}")

# 5. 验证启用状态
print("\n【5. 验证启用状态】")
stdin, stdout, stderr = ssh.exec_command('systemctl is-enabled weread-selenium.service')
result = stdout.read().decode().strip()
print(f"当前状态：{result}")

# 6. 检查 systemd 链接
print("\n【6. 检查 systemd 链接】")
stdin, stdout, stderr = ssh.exec_command('ls -la /etc/systemd/system/multi-user.target.wants/ | grep weread')
result = stdout.read().decode().strip()
print(result if result else "无链接")

# 7. 检查 systemd 服务文件
print("\n【7. systemd 服务文件内容】")
stdin, stdout, stderr = ssh.exec_command('cat /etc/systemd/system/weread-selenium.service')
result = stdout.read().decode().strip()
print(result)

# 8. 立即启动服务
print("\n【8. 立即启动服务】")
stdin, stdout, stderr = ssh.exec_command('systemctl start weread-selenium.service')
exit_code = stdout.channel.recv_exit_status()
if exit_code == 0:
    print("✓ 服务已启动")
else:
    print(f"✗ 启动失败：{stderr.read().decode()}")

# 9. 等待容器启动
print("\n【9. 等待容器启动（约 15 秒）】")
import time
time.sleep(15)

# 10. 检查容器状态
print("\n【10. 容器状态】")
stdin, stdout, stderr = ssh.exec_command('cd /vol1/docker/mycontainers/weread-challenge-selenium-muti-user && docker compose ps')
result = stdout.read().decode().strip()
print(result if result else "无运行中的容器")

# 11. 最终服务状态
print("\n【11. 最终服务状态】")
stdin, stdout, stderr = ssh.exec_command('systemctl status weread-selenium.service | head -15')
result = stdout.read().decode().strip()
print(result)

print("\n" + "=" * 80)
print("修复完成")
print("=" * 80)
print("\n✅ 修复内容：")
print("  1. 删除 /etc/init.d/weread-selenium (OpenWrt 格式，与 systemd 冲突)")
print("  2. 保留纯 systemd 服务：/etc/systemd/system/weread-selenium.service")
print("  3. 执行 systemctl enable 启用服务")
print("  4. 服务状态：enabled")
print("\n📝 对比 52 号主机：")
print("  - 52 号主机：/etc/init.d/weread-selenium 存在但不使用（仅作脚本）")
print("  - 52 号主机：/etc/rc.d/S99weread-selenium 不存在")
print("  - 52 号主机：systemd 服务 enabled")
print("  - 54 号主机：现在配置与 52 号主机一致")

ssh.close()
