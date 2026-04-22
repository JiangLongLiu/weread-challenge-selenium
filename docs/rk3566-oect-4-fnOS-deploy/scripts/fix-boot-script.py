#!/usr/bin/env python3
"""修复开机启动脚本（Debian systemd 格式）"""
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(hostname='192.168.123.54', port=22, username='root', password='1234567890')

print("=" * 80)
print("修复开机启动脚本")
print("=" * 80)

# 创建 systemd 服务文件
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
ExecStart=/bin/bash -c "cd /vol1/docker/mycontainers/weread-challenge-selenium-muti-user && docker compose up -d selenium"
ExecStop=/bin/bash -c "cd /vol1/docker/mycontainers/weread-challenge-selenium-muti-user && docker compose down"

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

# 启用服务
print("\n【3. 启用开机自启动】")
stdin, stdout, stderr = ssh.exec_command('systemctl enable weread-selenium.service')
exit_code = stdout.channel.recv_exit_status()
if exit_code == 0:
    print("✓ 开机自启动已启用")
else:
    print(f"✗ 启用失败：{stderr.read().decode()}")

# 启动服务
print("\n【4. 启动服务（立即执行）】")
stdin, stdout, stderr = ssh.exec_command('systemctl start weread-selenium.service')
exit_code = stdout.channel.recv_exit_status()
if exit_code == 0:
    print("✓ 服务已启动")
else:
    print(f"✗ 启动失败：{stderr.read().decode()}")

# 检查服务状态
print("\n【5. 检查服务状态】")
stdin, stdout, stderr = ssh.exec_command('systemctl status weread-selenium.service | head -15')
result = stdout.read().decode().strip()
print(result)

# 等待容器启动
print("\n【6. 等待容器启动（约 10 秒）】")
import time
time.sleep(10)

# 检查容器状态
print("\n【7. 检查容器状态】")
stdin, stdout, stderr = ssh.exec_command('cd /vol1/docker/mycontainers/weread-challenge-selenium-muti-user && docker compose ps')
result = stdout.read().decode().strip()
print(result if result else "无运行中的容器")

# 检查 VNC 端口
print("\n【8. 检查 VNC 端口】")
stdin, stdout, stderr = ssh.exec_command('netstat -tlnp | grep 7900')
result = stdout.read().decode().strip()
print(result if result else "7900 端口未监听")

print("\n" + "=" * 80)
print("修复完成")
print("=" * 80)

ssh.close()
