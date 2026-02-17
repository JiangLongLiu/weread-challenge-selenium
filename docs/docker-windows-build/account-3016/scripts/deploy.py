#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
本地 Docker 部署脚本 (account-3016)

功能：
1. 将 docker-compose.yml 复制到工作目录
2. 启动 Docker 容器

使用：
    python docs/docker-windows-build/account-3016/scripts/deploy.py

工作目录：E:\dockers\fork-workout-cool
"""

import os
import shutil
import subprocess

# 配置路径
SOURCE_DIR = r'E:\Qoder_workspace\weread-challenge-selenium\docs\docker-windows-build\account-3016'
WORK_DIR = r'E:\dockers\weread-challenge-selenium-3016'
DOCKER_COMPOSE_SOURCE = os.path.join(SOURCE_DIR, 'docker-compose.yml')
WORK_DOCKER_COMPOSE = os.path.join(WORK_DIR, 'docker-compose.yml')
WORK_DATA_DIR = os.path.join(WORK_DIR, 'data')


def deploy():
    print("=" * 50)
    print("本地 Docker 部署开始 (account-3016)")
    print("=" * 50)

    # 1. 确保工作目录存在
    print(f"\n[步骤 1/4] 创建工作目录...")
    if not os.path.exists(WORK_DIR):
        os.makedirs(WORK_DIR)
        print(f"创建目录: {WORK_DIR}")
    
    if not os.path.exists(WORK_DATA_DIR):
        os.makedirs(WORK_DATA_DIR)
        print(f"创建数据目录: {WORK_DATA_DIR}")

    # 2. 复制 docker-compose.yml (强制覆盖)
    print(f"\n[步骤 2/4] 复制 docker-compose.yml (强制覆盖)...")
    if os.path.exists(WORK_DOCKER_COMPOSE):
        os.remove(WORK_DOCKER_COMPOSE)
    shutil.copy(DOCKER_COMPOSE_SOURCE, WORK_DOCKER_COMPOSE)
    print(f"复制: {DOCKER_COMPOSE_SOURCE} -> {WORK_DOCKER_COMPOSE}")

    # 3. 删除旧容器
    print(f"\n[步骤 3/4] 删除旧容器...")
    try:
        subprocess.run(
            ['docker', 'compose', '-f', WORK_DOCKER_COMPOSE, 'down'],
            cwd=WORK_DIR,
            capture_output=True,
            text=True
        )
        print("旧容器已删除")
    except Exception as e:
        print(f"删除旧容器: {e}")

    # 4. 启动容器并检查状态
    print(f"\n[步骤 4/4] 启动容器并检查状态...")
    result = subprocess.run(
        ['docker', 'compose', '-f', WORK_DOCKER_COMPOSE, 'up', '-d'],
        cwd=WORK_DIR,
        capture_output=True,
        text=True
    )
    
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    if result.returncode == 0:
        print("\n容器启动成功!")
    else:
        print(f"\n容器启动失败，退出码: {result.returncode}")

    print("\n容器状态:")
    subprocess.run(['docker', 'ps', '--filter', 'name=weread-challenge-selenium-3016', '--format', 'table {{.Names}}\t{{.Status}}'])

    print("\n" + "=" * 50)
    print("部署完成!")
    print("=" * 50)
    print(f"\nVNC 界面: http://localhost:7900")
    print(f"VNC 密码: 111111")
    print(f"数据目录: {WORK_DATA_DIR}")


if __name__ == '__main__':
    deploy()