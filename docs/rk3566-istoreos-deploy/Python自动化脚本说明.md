# Python 自动化脚本说明

## 概述
本脚本用于实现自动化部署，通过读取密码文件中的凭证信息，无需人工输入密码即可完成 SSH 连接和文件上传。

## 文件位置
`docs/rk3566-istoreos-deploy/scripts/ssh_scp_util.py`

## 依赖安装
```bash
pip install pandas paramiko
```

## 脚本功能

### 1. 密码读取
从 Excel 文件 `password.xls` 读取主机凭证：
- IP 地址
- 用户名
- 密码
- SSH 端口

### 2. SSH 连接
使用 paramiko 库建立 SSH 连接：
- 自动读取密码
- 支持自定义端口
- 错误处理和重试机制

### 3. SCP 文件上传
实现文件上传功能：
- **上传本地 docker-compose.yml 到目标主机**
- 自动创建目标目录

### 4. 远程命令执行
在远程主机上执行命令：
- 创建目录
- 启动容器
- 查看状态

## 使用方法

### 前提条件
1. 在 `docs/rk3566-istoreos-deploy/docker-compose.yml` 中编辑好配置
2. 安装依赖：`pip install pandas paramiko`

### 基本用法
```bash
python docs/rk3566-istoreos-deploy/scripts/ssh_scp_util.py
```

### 脚本会自动执行以下操作：
1. 读取 password.xls 获取主机凭证
2. 建立 SSH 连接
3. 创建远程部署目录
4. **上传本地 docker-compose.yml** 到远程主机
5. 启动 Docker 容器
6. 验证部署状态

## 源码结构

```python
# 主要函数
def read_password_from_excel(excel_path):
    """从 Excel 读取密码"""

def connect_ssh(host, port, username, password):
    """建立 SSH 连接"""

def upload_file(ssh_client, local_file, remote_path):
    """上传文件"""

def execute_command(ssh_client, command):
    """执行远程命令"""

def deploy():
    """主部署流程"""
```

## 自定义配置

### 修改目标主机
编辑 `docs/rk3566-istoreos-deploy/password.xls` 文件

### 修改部署目录
在脚本中修改 `REMOTE_DIR` 变量：
```python
REMOTE_DIR = "/mnt/sata1-1/docker/mycontainers/weread-challenge-selenium"
```

## 错误处理

脚本包含以下错误处理：
- Excel 文件读取失败
- SSH 连接超时
- 文件传输失败
- 命令执行失败

## 调试模式

如需查看详细日志，可以在脚本中添加：
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 相关文档
- [部署操作手册](./部署操作手册.md)
- [故障排查指南](./故障排查指南.md)
