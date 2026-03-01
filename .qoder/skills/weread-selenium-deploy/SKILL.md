---
name: weread-selenium-deploy
description: RK3566 iStoreOS 微信读书多用户部署全流程。包含部署脚本、开机启动、定时任务、VNC/Xvfb 故障排查。使用于 RK3566、iStoreOS、Docker 部署、微信读书自动化、多用户隔离、Selenium Grid 等场景。
---

# WeRead Selenium 部署

## 快速开始

### 1. 部署

```bash
python docs/rk3566-muti-user-deploy/scripts/ssh_scp_util.py
```

### 2. 检查状态

```bash
python docs/rk3566-muti-user-deploy/scripts/check-status.py
```

## 核心脚本

| 脚本 | 用途 |
|------|------|
| `ssh_scp_util.py` | 自动化部署（含开机启动配置）|
| `check-status.py` | 检查容器状态、定时任务、数据目录 |
| `check_vnc.py` | 检查 VNC 服务状态 |
| `pull_image.py` | 拉取 Docker 镜像（自动读取 docker-compose.yml 版本）|

## 开机启动

### 脚本位置
- 脚本：`/etc/init.d/weread-selenium`
- 链接：`/etc/rc.d/S99weread-selenium`

### 启动流程
1. 等待 180 秒（避免 RK3566 CPU 卡死）
2. 等待 Docker 就绪
3. **清理 X11 资源**：`rm -f /tmp/.X*-lock /tmp/.X11-unix/X*`
4. 启动 Selenium 容器

### 关键配置（docker-compose.yml）
```yaml
environment:
  - DISPLAY_NUM=98        # 固定显示号，避免冲突
  - SE_SCREEN_WIDTH=1920
  - SE_SCREEN_HEIGHT=1080
  - SE_START_XVFB=true
  - SE_START_VNC=true
```

## 定时任务

### 任务配置
| 用户 | 服务 | 时间 |
|------|------|------|
| liujl4735 | app-1 | 00:00, 06:00, 13:00, 19:00 |
| liujl3016 | app-2 | 01:10, 07:10, 14:10, 20:10 |
| jpx155 | app-3 | 02:20, 08:20, 15:20, 21:20 |
| jpx181 | app-4 | 03:30, 09:30, 16:30, 22:30 |

### 任务存储
- 位置：`/var/spool/cron/crontabs/root`
- 定义：`ssh_scp_util.py` 第 177-216 行
- 防重复：部署时过滤关键词 `weread`、`selenium-muti-user`、`account-4735`

## VNC 故障排查

### 常见问题：VNC 白板

**原因**：显示号冲突
- X11 socket 残留占用显示号
- 默认 :99 被其他进程占用

**解决方案**：
1. 设置固定显示号 `DISPLAY_NUM=98`
2. 开机清理 X11 资源

**排查命令**：
```bash
# 检查 VNC 状态
python docs/rk3566-muti-user-deploy/scripts/调试/check_vnc.py

# 检查开机日志
python docs/rk3566-muti-user-deploy/scripts/工具/check_boot_log.py

# 手动检查
docker exec selenium-weread-challenge-selenium-muti-user ps aux | grep -E "xvfb|vnc"
```

## 部署配置

### 用户映射
| 用户名 | 服务名 | 数据目录 |
|--------|--------|----------|
| liujl4735 | app-1 | data/liujl4735 |
| liujl3016 | app-2 | data/liujl3016 |
| jpx155 | app-3 | data/jpx155 |
| jpx181 | app-4 | data/jpx181 |

### 环境变量
- `WEREAD_REMOTE_BROWSER=http://127.0.0.1:4444`
- `WEREAD_USER=用户名`
- `WEREAD_DURATION=68`

## 常用命令

```bash
# 手动启动 selenium
cd /mnt/sata1-1/docker/mycontainers/weread-challenge-selenium-muti-user
docker compose up -d selenium

# 手动启动用户容器
docker compose up app-1 -d

# 查看日志
docker compose logs -f app-1

# 停止容器
docker compose stop app-1
```

## 参考文档

- [README.md](docs/rk3566-muti-user-deploy/README.md) - 完整部署文档
- [docker-compose.yml](docs/rk3566-muti-user-deploy/docker-compose.yml) - 容器配置
