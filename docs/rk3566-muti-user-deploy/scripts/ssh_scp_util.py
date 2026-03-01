#!/usr/bin/env python3
"""
4用户远程部署脚本 - 无人值守版本
自动从 password.xls 读取 SSH 凭据
"""

import pandas as pd
import paramiko
from scp import SCPClient
import os

# 配置
PASSWORD_FILE = r'E:\Qoder_workspace\weread-challenge-selenium\docs\rk3566-muti-user-deploy\password.xls'
LOCAL_DIR = r'E:\Qoder_workspace\weread-challenge-selenium\docs\rk3566-muti-user-deploy'
REMOTE_DIR = "/mnt/sata1-1/docker/mycontainers/weread-challenge-selenium-muti-user"


def get_credentials():
    """从 Excel 读取 SSH 凭据"""
    df = pd.read_excel(PASSWORD_FILE)
    row = df.iloc[0]
    return {
        'host': str(row['IP地址']).strip(),
        'port': int(row['SSH端口']),
        'username': str(row['用户名']).strip(),
        'password': str(row['密码']).strip()
    }


def create_ssh_client(cred):
    """创建 SSH 连接"""
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(
        hostname=cred['host'],
        port=cred['port'],
        username=cred['username'],
        password=cred['password']
    )
    return client


def deploy():
    """执行部署"""
    print("=" * 60)
    print("RK3566 4用户微信读书助手部署")
    print("=" * 60)
    
    # 读取凭据
    print("\n[1/9] 读取 SSH 凭据...")
    cred = get_credentials()
    print(f"  主机: {cred['host']}:{cred['port']}")
    print(f"  用户: {cred['username']}")
    
    # 连接 SSH
    print("\n[2/9] 连接远程主机...")
    ssh = create_ssh_client(cred)
    print("  连接成功")
    
    try:
        # 关闭现有容器
        print("\n[3/9] 关闭现有容器...")
        ssh.exec_command(f"cd {REMOTE_DIR} && docker compose down 2>/dev/null")
        print("  ✓ 已关闭")
        
        # 创建远程目录
        print("\n[4/9] 创建远程工作目录...")
        ssh.exec_command(f"mkdir -p {REMOTE_DIR}")
        
        # 上传文件
        print("\n[5/9] 上传部署文件...")
        with SCPClient(ssh.get_transport()) as scp:
            scp.put(f"{LOCAL_DIR}/docker-compose.yml", f"{REMOTE_DIR}/docker-compose.yml")
            print("  ✓ docker-compose.yml")
        
        # 创建用户数据目录（批量执行）
        print("\n[6/9] 创建用户数据目录...")
        users = ['liujl4735', 'liujl3016', 'jpx155', 'jpx181']
        mkdir_cmd = " && ".join([f"mkdir -p {REMOTE_DIR}/data/{user}" for user in users])
        stdin, stdout, stderr = ssh.exec_command(mkdir_cmd)
        stdout.channel.recv_exit_status()
        for user in users:
            print(f"  ✓ {user}")
        
        # 配置定时任务
        print("\n[7/9] 配置定时任务...")
        setup_cron(ssh)
        
        # 启动容器（仅启动 selenium，所有用户容器由定时任务启动）
        print("\n[8/9] 启动 selenium 容器...")
        max_retries = 3
        for attempt in range(max_retries):
            stdin, stdout, stderr = ssh.exec_command(f"cd {REMOTE_DIR} && docker compose up -d selenium")
            exit_code = stdout.channel.recv_exit_status()
            if exit_code == 0:
                print(f"  ✓ selenium 已启动 (尝试 {attempt + 1}/{max_retries})")
                break
            else:
                err = stderr.read().decode()
                if err:
                    print(f"  警告 (尝试 {attempt + 1}/{max_retries}): {err[:200]}")
                if attempt < max_retries - 1:
                    import time
                    time.sleep(2)
        else:
            print("  ✗ selenium 启动失败，请手动检查")
        
        print("  ℹ 所有用户容器将在定时任务触发时自动启动")
        
        # 配置开机自启动
        print("\n[9/9] 配置 Selenium 开机自启动...")
        setup_autostart(ssh)
        
        print("\n" + "=" * 60)
        print("部署完成!")
        print("=" * 60)
        print(f"\n工作目录: {REMOTE_DIR}")
        print(f"VNC 地址: http://{cred['host']}:7900")
        print(f"\n用户时间表:")
        print("  liujl4735: 00:00, 06:00, 13:00, 19:00")
        print("  liujl3016: 01:10, 07:10, 14:10, 20:10")
        print("  jpx155:    02:20, 08:20, 15:20, 21:20")
        print("  jpx181:    03:30, 09:30, 16:30, 22:30")
        
    finally:
        ssh.close()


def setup_autostart(ssh):
    """配置 Selenium 开机自启动（OpenWrt 格式）"""
    # OpenWrt procd 格式的启动脚本
    script_lines = [
        '#!/bin/sh /etc/rc.common',
        '# WeRead Selenium Auto Start',
        '',
        'START=99',
        'STOP=10',
        '',
        'start() {',
        '    echo "Starting WeRead Selenium..."',
        '    echo "Waiting 180 seconds for system to stabilize..."',
        '    sleep 180',
        '    while ! docker ps >/dev/null 2>&1; do',
        '        sleep 2',
        '    done',
        f'    cd {REMOTE_DIR} && docker compose up -d selenium',
        '}',
        '',
        'stop() {',
        '    echo "Stopping WeRead Selenium..."',
        f'    cd {REMOTE_DIR} && docker compose down',
        '}',
    ]
    script_content = '\n'.join(script_lines)
    
    # 上传并配置启动脚本
    cmd = f"""cat > /etc/init.d/weread-selenium << 'EOF'
{script_content}
EOF
chmod +x /etc/init.d/weread-selenium
/etc/init.d/weread-selenium enable
"""
    stdin, stdout, stderr = ssh.exec_command(cmd)
    exit_code = stdout.channel.recv_exit_status()
    
    # 检查是否成功创建开机链接
    stdin, stdout, stderr = ssh.exec_command("ls /etc/rc.d/S99weread-selenium 2>/dev/null")
    if stdout.read().decode().strip():
        print("  ✓ 开机自启动已配置")
        print("  ℹ 重启后将自动启动 Selenium 容器")
    else:
        print("  警告: 开机链接未创建，尝试手动创建...")
        ssh.exec_command("ln -sf /etc/init.d/weread-selenium /etc/rc.d/S99weread-selenium")
        print("  ✓ 已手动创建开机链接")


def setup_cron(ssh):
    """配置定时任务"""
    # 构建完整的 crontab 内容（启动后70分钟自动停止并清理会话）
    cron_content = """# weread-multi: liujl4735
0 0 * * * cd {dir} && docker compose up app-1 -d && (sleep 4200 && docker compose stop app-1 && docker restart weread-challenge-selenium-muti-user-selenium-1) &
0 6 * * * cd {dir} && docker compose up app-1 -d && (sleep 4200 && docker compose stop app-1 && docker restart weread-challenge-selenium-muti-user-selenium-1) &
0 13 * * * cd {dir} && docker compose up app-1 -d && (sleep 4200 && docker compose stop app-1 && docker restart weread-challenge-selenium-muti-user-selenium-1) &
0 19 * * * cd {dir} && docker compose up app-1 -d && (sleep 4200 && docker compose stop app-1 && docker restart weread-challenge-selenium-muti-user-selenium-1) &
# weread-multi: liujl3016
10 1 * * * cd {dir} && docker compose up app-2 -d && (sleep 4200 && docker compose stop app-2 && docker restart weread-challenge-selenium-muti-user-selenium-1) &
10 7 * * * cd {dir} && docker compose up app-2 -d && (sleep 4200 && docker compose stop app-2 && docker restart weread-challenge-selenium-muti-user-selenium-1) &
10 14 * * * cd {dir} && docker compose up app-2 -d && (sleep 4200 && docker compose stop app-2 && docker restart weread-challenge-selenium-muti-user-selenium-1) &
10 20 * * * cd {dir} && docker compose up app-2 -d && (sleep 4200 && docker compose stop app-2 && docker restart weread-challenge-selenium-muti-user-selenium-1) &
# weread-multi: jpx155
20 2 * * * cd {dir} && docker compose up app-3 -d && (sleep 4200 && docker compose stop app-3 && docker restart weread-challenge-selenium-muti-user-selenium-1) &
20 8 * * * cd {dir} && docker compose up app-3 -d && (sleep 4200 && docker compose stop app-3 && docker restart weread-challenge-selenium-muti-user-selenium-1) &
20 15 * * * cd {dir} && docker compose up app-3 -d && (sleep 4200 && docker compose stop app-3 && docker restart weread-challenge-selenium-muti-user-selenium-1) &
20 21 * * * cd {dir} && docker compose up app-3 -d && (sleep 4200 && docker compose stop app-3 && docker restart weread-challenge-selenium-muti-user-selenium-1) &
# weread-multi: jpx181
30 3 * * * cd {dir} && docker compose up app-4 -d && (sleep 4200 && docker compose stop app-4 && docker restart weread-challenge-selenium-muti-user-selenium-1) &
30 9 * * * cd {dir} && docker compose up app-4 -d && (sleep 4200 && docker compose stop app-4 && docker restart weread-challenge-selenium-muti-user-selenium-1) &
30 16 * * * cd {dir} && docker compose up app-4 -d && (sleep 4200 && docker compose stop app-4 && docker restart weread-challenge-selenium-muti-user-selenium-1) &
30 22 * * * cd {dir} && docker compose up app-4 -d && (sleep 4200 && docker compose stop app-4 && docker restart weread-challenge-selenium-muti-user-selenium-1) &
# weread-multi: daily cleanup (screenshots and logs)
59 23 * * * cd {dir} && find data -name 'screenshot-*.png' -delete && find data -name 'output.log' -delete
""".format(dir=REMOTE_DIR)
    
    # 清理旧任务并添加新任务（一次性执行）
    # 过滤掉所有微信读书相关任务：weread-multi、weread、selenium-muti-user、account-4735
    cmd = f"(crontab -l 2>/dev/null | grep -v -E 'weread|selenium-muti-user|account-4735'; echo '{cron_content}') | crontab -"
    stdin, stdout, stderr = ssh.exec_command(cmd)
    
    # 等待命令完成
    exit_code = stdout.channel.recv_exit_status()
    if exit_code != 0:
        err = stderr.read().decode()
        if err:
            print(f"  警告: {err}")
    
    print("  ✓ 16个定时任务已配置")


if __name__ == "__main__":
    deploy()
