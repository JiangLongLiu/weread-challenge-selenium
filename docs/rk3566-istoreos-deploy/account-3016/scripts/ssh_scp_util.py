#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RK3566 iStoreOS 自动化部署脚本 (account-3016)

功能：
1. 从 password.xls 读取 SSH 密码
2. 通过 SSH 连接到 RK3566 主机
3. 创建远程部署目录
4. 上传本地 docker-compose.yml 到远程主机
5. 启动 Docker 容器

使用：
    python docs/rk3566-istoreos-deploy/account-3016/scripts/ssh_scp_util.py

注意：
    请先在 account-3016 目录下编辑好 docker-compose.yml 文件，
    脚本会读取本地 docker-compose.yml 并上传到远程主机。
"""

import os
import sys
import time
import pandas as pd
import paramiko
import yaml
from paramiko import SSHClient, AutoAddPolicy

# 配置路径 - 使用绝对路径
PASSWORD_FILE = r'E:\Qoder_workspace\weread-challenge-selenium\docs\rk3566-istoreos-deploy\account-3016\password.xls'
DOCKER_COMPOSE_SOURCE = r'E:\Qoder_workspace\weread-challenge-selenium\docs\rk3566-istoreos-deploy\account-3016\docker-compose.yml'
REMOTE_DIR = '/mnt/sata1-1/docker/mycontainers/weread-challenge-selenium-3016'


def read_password_from_excel(excel_path):
    """
    从 Excel 文件读取主机密码

    Args:
        excel_path: Excel 文件路径

    Returns:
        dict: 包含主机信息的字典
    """
    try:
        df = pd.read_excel(excel_path)
        # 获取第一行数据
        row = df.iloc[0]
        return {
            'host': row['IP地址'],
            'username': row['用户名'],
            'password': str(row['密码']),
            'port': int(row['SSH端口']),
            'remark': row['备注']
        }
    except Exception as e:
        print(f"读取密码文件失败: {e}")
        sys.exit(1)


def connect_ssh(host, port, username, password):
    """
    建立 SSH 连接

    Args:
        host: 主机地址
        port: 端口
        username: 用户名
        password: 密码

    Returns:
        SSHClient: SSH 客户端对象
    """
    print(f"正在连接到 {host}:{port}...")
    client = SSHClient()
    client.set_missing_host_key_policy(AutoAddPolicy())

    try:
        client.connect(
            hostname=host,
            port=port,
            username=username,
            password=password,
            timeout=30
        )
        print("SSH 连接成功!")
        return client
    except Exception as e:
        print(f"SSH 连接失败: {e}")
        sys.exit(1)


def execute_command(ssh_client, command, timeout=30):
    """
    执行远程命令

    Args:
        ssh_client: SSH 客户端
        command: 命令字符串
        timeout: 超时时间（秒）

    Returns:
        tuple: (stdout, stderr, exit_code)
    """
    print(f"执行命令: {command}")
    stdin, stdout, stderr = ssh_client.exec_command(command, timeout=timeout)
    exit_code = stdout.channel.recv_exit_status()
    stdout_text = stdout.read().decode('utf-8')
    stderr_text = stderr.read().decode('utf-8')
    return stdout_text, stderr_text, exit_code


def create_remote_directory(ssh_client, remote_dir):
    """
    创建远程目录

    Args:
        ssh_client: SSH 客户端
        remote_dir: 远程目录路径
    """
    print(f"创建远程目录: {remote_dir}")
    cmd = f'mkdir -p {remote_dir}'
    stdout, stderr, code = execute_command(ssh_client, cmd)
    if code != 0:
        print(f"创建目录失败: {stderr}")
        sys.exit(1)
    print("目录创建成功")

    # 创建 data 子目录
    data_dir = f'{remote_dir}/data'
    print(f"创建数据目录: {data_dir}")
    cmd = f'mkdir -p {data_dir}'
    stdout, stderr, code = execute_command(ssh_client, cmd)
    if code != 0:
        print(f"创建data目录失败: {stderr}")
    else:
        print("data目录创建成功")


def upload_file(ssh_client, local_file, remote_path):
    """
    上传文件到远程主机

    Args:
        ssh_client: SSH 客户端
        local_file: 本地文件路径
        remote_path: 远程文件路径
    """
    print(f"上传文件: {local_file} -> {remote_path}")

    try:
        sftp = ssh_client.open_sftp()
        sftp.put(local_file, remote_path)
        sftp.close()
        print("文件上传成功!")
    except Exception as e:
        print(f"文件上传失败: {e}")
        sys.exit(1)


def upload_docker_compose(ssh_client, local_file, remote_dir):
    """
    上传本地 docker-compose.yml 到远程主机

    Args:
        ssh_client: SSH 客户端
        local_file: 本地 docker-compose.yml 文件路径
        remote_dir: 远程目录路径
    """
    if not os.path.exists(local_file):
        print(f"错误: 本地文件不存在: {local_file}")
        print("请先在项目根目录创建/编辑 docker-compose.yml 文件")
        sys.exit(1)

    remote_path = f'{remote_dir}/docker-compose.yml'
    print(f"上传文件: {local_file} -> {remote_path}")

    try:
        sftp = ssh_client.open_sftp()
        
        # 强制覆盖：直接 put 会覆盖已存在的文件
        sftp.put(local_file, remote_path)
        sftp.close()
        
        # 验证上传
        stdin, stdout, stderr = ssh_client.exec_command(f'ls -la {remote_path}')
        print("验证远程文件:", stdout.read().decode())
        print("docker-compose.yml 上传成功 (强制覆盖)!")
    except Exception as e:
        print(f"文件上传失败: {e}")
        sys.exit(1)


def start_containers(ssh_client, remote_dir):
    """
    在远程主机上启动 Docker 容器

    Args:
        ssh_client: SSH 客户端
        remote_dir: 远程目录
    """
    print("启动 Docker 容器...")

    # 先删除现有容器
    print("删除现有容器...")
    cmd = f'cd {remote_dir} && docker compose down'
    stdin, stdout, stderr = ssh_client.exec_command(cmd, timeout=120)
    print("STDERR:", stderr.read().decode())

    # 检查镜像是否存在，不存在时才 pull
    print("检查镜像是否存在...")
        
    # 读取 docker-compose.yml 获取镜像名称
    with open(DOCKER_COMPOSE_SOURCE, 'r', encoding='utf-8') as f:
        compose_config = yaml.safe_load(f)
        
    app_image = compose_config['services']['app']['image']
    selenium_image = compose_config['services']['selenium']['image']
        
    # 检查镜像是否存在
    stdin, stdout, stderr = ssh_client.exec_command(f'docker images -q {app_image}')
    app_exists = stdout.read().decode().strip()
        
    stdin, stdout, stderr = ssh_client.exec_command(f'docker images -q {selenium_image}')
    selenium_exists = stdout.read().decode().strip()
        
    if not app_exists or not selenium_exists:
        print("镜像不存在，正在拉取...")
        stdin, stdout, stderr = ssh_client.exec_command(f'docker compose -f {remote_dir}/docker-compose.yml pull', timeout=600)
        print("拉取结果:", stderr.read().decode())
    else:
        print("镜像已存在，跳过拉取")
        
    # 启动容器
    print("启动容器...")
    # 只启动 app 服务，跳过 selenium（复用 4735 的 Selenium）
    stdin, stdout, stderr = ssh_client.exec_command(f'cd {remote_dir} && docker compose up -d app', timeout=300)
    exit_code = stdout.channel.recv_exit_status()
    stdout_text = stdout.read().decode('utf-8')
    stderr_text = stderr.read().decode('utf-8')

    if stdout_text:
        print(stdout_text)
    if stderr_text:
        print("STDERR:", stderr_text)

    if exit_code != 0:
        print(f"启动容器失败，退出码: {exit_code}")
    else:
        print("容器启动成功")


def check_container_status(ssh_client):
    """
    检查容器运行状态

    Args:
        ssh_client: SSH 客户端
    """
    print("检查容器状态...")
    stdout, stderr, code = execute_command(ssh_client, 'docker ps --format "table {{.Names}}\\t{{.Status}}\\t{{.Ports}}"')
    print(stdout)


def deploy():
    """主部署流程"""
    print("=" * 50)
    print("RK3566 iStoreOS 自动化部署开始")
    print("=" * 50)

    # 1. 读取密码
    print("\n[步骤 1/6] 读取主机密码...")
    host_info = read_password_from_excel(PASSWORD_FILE)
    print(f"主机: {host_info['host']} ({host_info['remark']})")
    print(f"用户: {host_info['username']}")

    # 2. SSH 连接
    print("\n[步骤 2/6] 建立 SSH 连接...")
    ssh_client = connect_ssh(
        host_info['host'],
        host_info['port'],
        host_info['username'],
        host_info['password']
    )

    try:
        # 3. 创建远程目录
        print("\n[步骤 3/6] 创建远程部署目录...")
        create_remote_directory(ssh_client, REMOTE_DIR)

        # 4. 上传 docker-compose.yml
        print("\n[步骤 4/6] 上传 docker-compose.yml...")
        upload_docker_compose(ssh_client, DOCKER_COMPOSE_SOURCE, REMOTE_DIR)

        # 5. 启动容器
        print("\n[步骤 5/6] 启动 Docker 容器...")
        start_containers(ssh_client, REMOTE_DIR)

        # 6. 检查状态
        print("\n[步骤 6/6] 检查容器状态...")
        time.sleep(5)  # 等待容器启动
        check_container_status(ssh_client)

        print("\n" + "=" * 50)
        print("部署完成!")
        print("=" * 50)
        print(f"\nVNC 界面: http://{host_info['host']}:7900")
        print("VNC 密码: secret")
        print(f"\n数据目录: {REMOTE_DIR}/data")
        print("请在 data/login.png 中扫描二维码登录微信读书")

    finally:
        ssh_client.close()
        print("\nSSH 连接已关闭")


if __name__ == '__main__':
    deploy()
