# RK3566 iStoreOS 微信读书助手部署

本目录包含将微信读书挑战助手部署到 RK3566 iStoreOS 主机的完整方案。

## 快速开始

### 前置条件
1. RK3566 iStoreOS 主机已安装 Docker 和 Docker Compose
2. 可通过网络访问主机 SSH（默认 22 端口）

### 部署步骤

```bash
# 1. 安装 Python 依赖
pip install pandas paramiko

# 2. 编辑 password.csv，填入 SSH 密码

# 3. 执行部署（会自动删除旧容器并重新部署）
python docs/rk3566-istoreos-deploy/account-3016/scripts/ssh_scp_util.py
```

### 首次登录
部署完成后，使用 VNC 访问 http://192.168.123.51:7900 ，扫描 data/login.png 二维码登录微信读书。

## 目录结构

```
account-3016/
├── README.md                  # 本文件
├── 快速开始.md                # 快速开始指南
├── docker-compose.yml         # Docker 配置
├── password.csv               # SSH 密码文件（不提交 Git）
└── scripts/
    └── ssh_scp_util.py       # 主部署脚本
```

## 配置说明

### docker-compose.yml 关键配置

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| WEREAD_DURATION | 每日阅读时长（分钟） | 68 |
| SE_VNC_PASSWORD | VNC 访问密码 | 111111 |

### 修改 VNC 密码
编辑 docker-compose.yml 中的 `SE_VNC_PASSWORD` 环境变量：
```yaml
environment:
  - SE_VNC_PASSWORD=你的密码
```

## 常用命令

```bash
# 重新部署（修改配置后执行）
python docs/rk3566-istoreos-deploy/account-3016/scripts/ssh_scp_util.py

# SSH 手动登录
ssh root@192.168.123.51

# 查看容器日志
docker logs -f weread-challenge-selenium-app-1

# 重启容器
docker restart weread-challenge-selenium-app-1
```

## 服务地址

| 服务 | 地址 |
|------|------|
| VNC 界面 | http://192.168.123.51:7900 |
| Selenium Grid | http://192.168.123.51:4444 |
| 数据目录 | /mnt/sata1-1/docker/mycontainers/weread-challenge-selenium-3016/data |

## 常见问题

### Q: VNC 显示 ERR_CONNECTION_CLOSED 错误？

**原因：** iStoreOS 宿主机可能配置了代理服务器，容器会继承宿主机的代理环境变量，导致无法正常访问微信读书网站。

**解决方案：** docker-compose.yml 中已配置清除代理环境变量：
```yaml
environment:
  - HTTP_PROXY=
  - HTTPS_PROXY=
  - http_proxy=
  - https_proxy=
```

如需使用代理，请修改上述环境变量为有效的代理地址。

### Q: VNC 密码不对？
修改 docker-compose.yml 中的 `SE_VNC_PASSWORD` 后重新部署。

### Q: 容器启动失败？
检查 Selenium 是否健康：`docker ps | grep selenium`

### Q: 如何修改阅读时长？
编辑 docker-compose.yml 中的 `WEREAD_DURATION=68`（分钟）
