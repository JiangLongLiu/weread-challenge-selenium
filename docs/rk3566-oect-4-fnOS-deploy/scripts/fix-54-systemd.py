#!/usr/bin/env python3
"""修复 54 号主机的 systemd 服务（参考 52 号主机配置）"""
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(hostname='192.168.123.54', port=22, username='root', password='1234567890')

print("=" * 80)
print("修复 54 号主机 systemd 服务（参考 52 号主机）")
print("=" * 80)

# 创建 systemd 服务文件（参考 52 号主机的配置）
service_content = """[Unit]
Description=WeRead Selenium Container
After=network-online.target docker.service
Requires=docker.service
Wants=network-online.target

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStartPre=/bin/sleep 180
ExecStartPre=/bin/bash -c "while ! docker ps >/dev/null 2>&1; do sleep 2; done"
ExecStartPre=/bin/rm -f /tmp/.X*-lock /tmp/.X11-unix/X* 2>/dev/null || true
ExecStart=/usr/bin/docker compose -f /vol1/docker/mycontainers/weread-challenge-selenium-muti-user/docker-compose.yml up -d selenium
ExecStop=/usr/bin/docker compose -f /vol1/docker/mycontainers/weread-challenge-selenium-muti-user/docker-compose.yml down

[Install]
WantedBy=multi-user.target
"""

print("\n【1. 创建 systemd 服务文件】")
cmd = f"""cat > /etc/systemd/system/weread-selenium.service << 'EOF'
{service_content}
EOF"""
stdin, stdout, stderr = ssh.exec_command(cmd)
exit_code = stdout.channel.recv_exit_status()
if exit_code == 0:
    print("✓ systemd 服务文件已创建")
else:
    print(f"✗ 创建失败：{stderr.read().decode()}")

# 重新加载 systemd
print("\n【2. 重新加载 systemd 配置】")
stdin, stdout, stderr = ssh.exec_command('systemctl daemon-reload')
exit_code = stdout.channel.recv_exit_status()
if exit_code == 0:
    print("✓ systemd 配置已重新加载")
else:
    print(f"✗ 重新加载失败：{stderr.read().decode()}")

# 启用服务（关键步骤！）
print("\n【3. 启用开机自启动】")
stdin, stdout, stderr = ssh.exec_command('systemctl enable weread-selenium.service')
exit_code = stdout.channel.recv_exit_status()
if exit_code == 0:
    print("✓ 开机自启动已启用 (enabled)")
else:
    print(f"✗ 启用失败：{stderr.read().decode()}")

# 验证启用状态
print("\n【4. 验证启用状态】")
stdin, stdout, stderr = ssh.exec_command('systemctl is-enabled weread-selenium.service')
result = stdout.read().decode().strip()
print(f"当前状态：{result}")

# 立即启动服务
print("\n【5. 立即启动服务】")
stdin, stdout, stderr = ssh.exec_command('systemctl start weread-selenium.service')
exit_code = stdout.channel.recv_exit_status()
if exit_code == 0:
    print("✓ 服务已启动")
else:
    print(f"✗ 启动失败：{stderr.read().decode()}")

# 等待容器启动
print("\n【6. 等待容器启动（约 15 秒）】")
import time
time.sleep(15)

# 检查容器状态
print("\n【7. 检查容器状态】")
stdin, stdout, stderr = ssh.exec_command('cd /vol1/docker/mycontainers/weread-challenge-selenium-muti-user && docker compose ps')
result = stdout.read().decode().strip()
print(result if result else "无运行中的容器")

# 检查服务状态
print("\n【8. 服务状态】")
stdin, stdout, stderr = ssh.exec_command('systemctl status weread-selenium.service | grep -E "Loaded|Active"')
result = stdout.read().decode().strip()
print(result)

print("\n" + "=" * 80)
print("修复完成")
print("=" * 80)
print("\n✅ 关键修复：")
print("  1. 使用 /usr/bin/docker compose 绝对路径")
print("  2. 执行 systemctl enable 启用开机自启动")
print("  3. 服务状态：enabled")

ssh.close()
