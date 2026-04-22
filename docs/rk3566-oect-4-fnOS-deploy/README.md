# RK3566-OECT-4-fnOS 4用户微信读书助手部署

4用户分时复用部署方案，支持 liujl4735、liujl3016、jpx155、jpx181 四个账号独立阅读。

部署于 RK3566-OECT-4-fnOS 主机。

## 快速开始

### 1. 部署

```bash
python docs/rk3566-oect-4-fnOS-deploy/scripts/ssh_scp_util.py
```

自动完成：
- 读取 password.csv 中的 SSH 凭据
- 上传 docker-compose.yml 到远程主机
- 创建4个用户的数据目录
- 配置16个定时任务（4用户×4时段）

### 2. 检查状态

```bash
python docs/rk3566-oect-4-fnOS-deploy/scripts/check-status.py
```

### 3. 首次登录

访问 VNC 界面扫码登录：
- 地址：http://192.168.123.54:7900
- 密码：111111

**登录时间窗口：**

| 用户 | 第1轮 | 第2轮 | 第3轮 | 第4轮 |
|------|-------|-------|-------|-------|
| liujl4735 | 00:00 | 06:00 | 13:00 | 19:00 |
| liujl3016 | 01:10 | 07:10 | 14:10 | 20:10 |
| jpx155 | 02:20 | 08:20 | 15:20 | 21:20 |
| jpx181 | 03:30 | 09:30 | 16:30 | 22:30 |

> 提示：容器在整点准时启动，浏览器和二维码约 2-3 分钟后就绪。如果错过时间窗口，可随时访问 VNC 查看状态，或手动执行 `docker compose up app-X -d` 重新启动容器。

> **错过时间窗口的应对：**
>
> | 情况 | 能否登录 | 操作 |
> |------|---------|------|
> | 容器运行中，二维码显示 | ✅ 可以 | 直接扫码 |
> | 容器运行中，页面已加载 | ✅ 可以 | 扫码或刷新页面 |
> | 容器已停止 | ⚠️ 需重启 | 手动执行 `docker compose up app-X -d` |

## 文件结构

### 本地文件

```
rk3566-oect-4-fnOS-deploy/
├── docker-compose.yml          # 容器编排配置
├── password.csv               # SSH 凭据（不提交Git）
├── README.md                 # 本文件
└── scripts/
    ├── ssh_scp_util.py        # 部署脚本（含开机启动配置）
    ├── check-status.py         # 状态检查脚本
    ├── start_selenium.py       # 手动启动 Selenium
    ├── weread-selenium.init   # 开机启动脚本模板
    ├── 调试/
    │   ├── debug_app1.py          # 调试 app-1 启动
    │   ├── check_vnc.py           # 检查 VNC 服务状态
    │   ├── check_vnc_detail.py    # VNC 详细诊断
    │   ├── check_xvfb.py          # 检查 Xvfb 启动问题
    │   ├── check_xvfb_error.py    # 检查 Xvfb 错误日志
    │   ├── check_xvfb_logs.py     # 检查 Xvfb 日志文件
    │   ├── test_xvfb.py           # 测试 Xvfb 启动
    │   ├── test_xvfb_manual.py    # 手动测试 Xvfb 启动
    │   └── test_xvfb_simple.py    # 简化测试 Xvfb 启动
    └── 工具/
        ├── pull_image.py           # 拉取 Docker 镜像
        ├── check_time_and_tasks.py # 检查时间和定时任务
        ├── check_boot_log.py       # 检查开机启动日志
        ├── check_containers.py     # 检查容器名称
        ├── setup-autostart.sh      # 开机自启动设置脚本
        └── weread-selenium.service # systemd 服务文件
```

### 远程主机（RK3566-OECT-4-fnOS）文件

```
/etc/systemd/system/weread-selenium.service  # systemd 服务文件（由 ssh_scp_util.py 创建）
/var/spool/cron/crontabs/root                # 定时任务存储
/vol1/docker/mycontainers/                   # Docker 工作目录
└── weread-challenge-selenium-muti-user/
    ├── docker-compose.yml
    └── data/
        ├── liujl4735/
        ├── liujl3016/
        ├── jpx155/
        └── jpx181/
```

**重要说明：**
- fnOS 使用 Debian systemd，**不使用** SysV 初始化脚本（`/etc/init.d/`）
- 开机启动由 systemd 服务管理，命令：`systemctl enable/disable weread-selenium.service`
- 部署脚本会自动配置 systemd 服务，无需手动干预

## 常用操作

### 手动启动阅读

```bash
# selenium
cd /vol1/docker/mycontainers/weread-challenge-selenium-muti-user && docker compose up -d selenium

# liujl4735
cd /vol1/docker/mycontainers/weread-challenge-selenium-muti-user && docker compose up app-1 -d

# liujl3016
cd /vol1/docker/mycontainers/weread-challenge-selenium-muti-user && docker compose up app-2 -d

# jpx155
cd /vol1/docker/mycontainers/weread-challenge-selenium-muti-user && docker compose up app-3 -d

# jpx181
cd /vol1/docker/mycontainers/weread-challenge-selenium-muti-user && docker compose up app-4 -d
```

### 手动停止阅读

```bash
# selenium
cd /vol1/docker/mycontainers/weread-challenge-selenium-muti-user && docker compose stop selenium

# liujl4735
cd /vol1/docker/mycontainers/weread-challenge-selenium-muti-user && docker compose stop app-1
# 模拟定时任务的停止流程（关键测试）
cd /vol1/docker/mycontainers/weread-challenge-selenium-muti-user && docker compose stop app-1 && docker restart weread-challenge-selenium-muti-user

# liujl3016
cd /vol1/docker/mycontainers/weread-challenge-selenium-muti-user && docker compose stop app-2

# jpx155
cd /vol1/docker/mycontainers/weread-challenge-selenium-muti-user && docker compose stop app-3

# jpx181
cd /vol1/docker/mycontainers/weread-challenge-selenium-muti-user && docker compose stop app-4
```

### 查看日志

```bash
cd /vol1/docker/mycontainers/weread-challenge-selenium-muti-user
docker compose logs -f app-1
docker compose logs -f app-2
docker compose logs -f app-3
docker compose logs -f app-4
```

### 停止所有容器

```bash
docker compose down
```

### 重新部署

```bash
python docs/rk3566-oect-4-fnOS-deploy/scripts/ssh_scp_util.py
```

### 更新 Selenium 镜像到最新版本

当容器重启或需要升级时，可手动更新 Selenium 镜像：

```bash
# 1. 停止所有容器
cd /vol1/docker/mycontainers/weread-challenge-selenium-muti-user
docker compose down

# 2. 拉取最新版本的 Selenium 镜像
docker pull selenium/standalone-chromium:latest

# 3. 查看本地镜像版本
docker images | grep selenium

# 4. 启动容器（使用新镜像）
docker compose up -d selenium

# 5. 检查容器状态
docker compose ps

# 6. 查看容器日志
docker compose logs -f selenium
```

**注意事项：**
- 更新镜像前建议先停止所有容器
- 拉取最新镜像后，容器会自动使用新版本
- 建议检查容器日志确认启动正常
- 如遇问题，可回退到稳定版本（如 147.0）

**回退到特定版本：**
```bash
# 拉取特定版本
docker pull selenium/standalone-chromium:147.0

# 修改 docker-compose.yml 中的镜像版本
# 然后重启容器
docker compose up -d selenium
```

### 管理开机启动

```bash
# 查看 systemd 服务文件
cat /etc/systemd/system/weread-selenium.service

# 手动启用开机启动
systemctl enable weread-selenium.service

# 手动禁用开机启动
systemctl disable weread-selenium.service

# 手动启动（带 180 秒延迟）
systemctl start weread-selenium.service

# 手动停止
systemctl stop weread-selenium.service

# 查看状态
systemctl status weread-selenium.service

# 查看启动日志
journalctl -u weread-selenium.service -f
```

**重要提示：**
- fnOS 是 Debian 系统，使用 systemd 管理开机启动
- **不要使用** `/etc/init.d/weread-selenium` 命令（OpenWrt 格式，与 systemd 冲突）
- 部署脚本会自动配置 systemd 服务并启用

## 注意事项

1. **VNC 共享**：4 用户共用一个 VNC 端口，需按时间窗口错开使用
2. **首次登录**：每个账号首次需手动扫码，后续自动保持登录状态
3. **阅读时长**：每次阅读 68 分钟，每日 4 次
4. **定时任务**：由 crontab 管理，共 17 个任务（16 个阅读 + 1 个清理）
   - 存储位置：`/var/spool/cron/crontabs/root`
   - 防重复机制：部署时自动清理旧任务

5. **数据清理**：每日 23:59 自动清理所有用户的截图（screenshot-*.png）和日志（output.log），保留 login.png
   - 清理范围：`data/*/screenshot-*.png`、`data/*/output.log`
   - 持久化机制：清理任务与其他定时任务一样存储在 `/var/spool/cron/crontabs/root`，主机重启后依然有效
   - 验证方法：`crontab -l | grep "daily cleanup"`

6. **systemd 服务**：fnOS 使用 Debian systemd 管理开机启动
   - 服务文件：`/etc/systemd/system/weread-selenium.service`
   - 启用状态：`systemctl is-enabled weread-selenium.service`（应显示 enabled）
   - **禁止使用**：`/etc/init.d/weread-selenium`（OpenWrt 格式，与 systemd 冲突）
   - 启动时间：约 4 分钟（含 180 秒系统稳定等待）

7. **镜像版本管理**：
   - 当前版本：`selenium/standalone-chromium:147.0`
   - 更新镜像：`docker pull selenium/standalone-chromium:latest`
   - 回退版本：`docker pull selenium/standalone-chromium:147.0`
   - 建议：生产环境使用稳定版本，测试环境可尝试最新版本

## 相关文档

- [scripts/ssh_scp_util.py](scripts/ssh_scp_util.py) - 自动化部署脚本（含 systemd 配置）
- [scripts/check-status.py](scripts/check-status.py) - 状态检查脚本
- [scripts/start_selenium.py](scripts/start_selenium.py) - 手动启动 Selenium
- [scripts/工具/check_time_and_tasks.py](scripts/工具/check_time_and_tasks.py) - 检查时间和定时任务
- [scripts/调试/debug_app1.py](scripts/调试/debug_app1.py) - 调试 app-1 启动
- [scripts/工具/pull_image.py](scripts/工具/pull_image.py) - 拉取 Docker 镜像

### systemd 相关脚本

- [scripts/工具/weread-selenium.service](scripts/工具/weread-selenium.service) - systemd 服务文件模板
- [scripts/fix-54-systemd-final.py](scripts/fix-54-systemd-final.py) - systemd 服务修复脚本
- [scripts/verify-container-start.py](scripts/verify-container-start.py) - 容器启动验证脚本

### VNC 故障排查脚本

- [scripts/调试/check_vnc.py](scripts/调试/check_vnc.py) - 检查 VNC 服务状态
- [scripts/调试/check_vnc_detail.py](scripts/调试/check_vnc_detail.py) - VNC 详细诊断
- [scripts/调试/check_xvfb.py](scripts/调试/check_xvfb.py) - 检查 Xvfb 启动问题
- [scripts/调试/check_xvfb_error.py](scripts/调试/check_xvfb_error.py) - 检查 Xvfb 错误日志
- [scripts/调试/check_xvfb_logs.py](scripts/调试/check_xvfb_logs.py) - 检查 Xvfb 日志文件
- [scripts/调试/test_xvfb.py](scripts/调试/test_xvfb.py) - 测试 Xvfb 启动
- [scripts/调试/test_xvfb_manual.py](scripts/调试/test_xvfb_manual.py) - 手动测试 Xvfb 启动
- [scripts/调试/test_xvfb_simple.py](scripts/调试/test_xvfb_simple.py) - 简化测试 Xvfb 启动
- [scripts/工具/check_boot_log.py](scripts/工具/check_boot_log.py) - 检查开机启动日志

## 开机启动流程

RK3566-OECT-4-fnOS（Debian）重启后，通过 systemd 服务自动启动 Selenium 容器：

```
主机重启
    ↓
systemd 启动 weread-selenium.service
    ↓
sleep 180（等待系统就绪）
    ↓
等待 Docker 就绪
    ↓
清理 X11 资源
    ↓
启动 Selenium 容器 (restart: unless-stopped)
```

**systemd 服务配置：**
- 服务文件：`/etc/systemd/system/weread-selenium.service`
- 启用命令：`systemctl enable weread-selenium.service`
- 启动命令：`systemctl start weread-selenium.service`
- 状态检查：`systemctl status weread-selenium.service`

**注意：**
- 服务配置了 `Type=oneshot` + `RemainAfterExit=yes`
- 容器异常重启由 docker-compose.yml 的 `restart: unless-stopped` 保证
- 用户容器通过定时任务启动，不需要开机自启动

**systemd 服务启用状态验证：**
```bash
# 检查服务是否启用（应显示 enabled）
systemctl is-enabled weread-selenium.service

# 检查 systemd 链接
ls -la /etc/systemd/system/multi-user.target.wants/ | grep weread
```

**常见问题：**
- 如果服务显示 `disabled`，执行 `systemctl enable weread-selenium.service`
- 如果存在 `/etc/init.d/weread-selenium` 文件（OpenWrt 格式），应删除以避免冲突

### X11 清理功能

```bash
rm -f /tmp/.X*-lock /tmp/.X11-unix/X* 2>/dev/null
```

### systemd 服务详解

**服务文件位置：**
```bash
/etc/systemd/system/weread-selenium.service
```

**服务配置内容：**
```ini
[Unit]
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
WantedBy: multi-user.target
```

**配置说明：**
- `Type=oneshot` + `RemainAfterExit=yes`：一次性服务，执行完成后保持状态
- `ExecStartPre=/bin/sleep 180`：等待 180 秒，确保系统完全稳定
- `ExecStartPre` 等待 Docker：循环检查 Docker 服务是否就绪
- `ExecStartPre` 清理 X11：清理旧的 X11 socket，防止显示号冲突
- `ExecStart`：启动 Selenium 容器
- `ExecStop`：停止所有容器

**启用状态验证：**
```bash
# 应显示 enabled
systemctl is-enabled weread-selenium.service

# 应显示 systemd 链接
ls -la /etc/systemd/system/multi-user.target.wants/ | grep weread
```

**为什么使用 systemd 而不是 SysV？**
- fnOS 基于 Debian，使用 systemd 作为初始化系统
- SysV 脚本（`/etc/init.d/*`）是 OpenWrt 格式，与 systemd 不兼容
- systemd 提供更好的依赖管理、日志记录和状态跟踪

## 定时任务详情

### 任务列表

| 用户 | 服务 | 定时规则 | 执行时间 |
|------|------|----------|----------|
| liujl4735 | app-1 | `0 0,6,13,19 * * *` | 00:00, 06:00, 13:00, 19:00 |
| liujl3016 | app-2 | `10 1,7,14,20 * * *` | 01:10, 07:10, 14:10, 20:10 |
| jpx155 | app-3 | `20 2,8,15,21 * * *` | 02:20, 08:20, 15:20, 21:20 |
| jpx181 | app-4 | `30 3,9,16,22 * * *` | 03:30, 09:30, 16:30, 22:30 |
| daily cleanup | - | `59 23 * * *` | 23:59 |

### 任务流程

每个阅读任务的执行流程：
```bash
# 1. 启动用户容器
docker compose up app-X -d

# 2. 等待 70 分钟（4200 秒）
sleep 4200

# 3. 停止用户容器
docker compose stop app-X

# 4. 重启 Selenium 清理会话
docker restart weread-challenge-selenium-muti-user
```

### 数据清理任务

```bash
# 每日 23:59 执行
cd /vol1/docker/mycontainers/weread-challenge-selenium-muti-user
find data -name 'screenshot-*.png' -delete
find data -name 'output.log' -delete
```

## 故障排查

### 容器无法启动

```bash
docker ps | grep weread
docker compose logs selenium
```

**解决方案：**

1. **检查容器状态**
```bash
docker compose ps
```

2. **查看容器日志**
```bash
docker compose logs selenium
```

3. **尝试重启容器**
```bash
docker restart weread-challenge-selenium-muti-user
```

4. **如果镜像有问题，更新到最新版本**
```bash
# 停止容器
docker compose down

# 拉取最新镜像
docker pull selenium/standalone-chromium:latest

# 启动容器
docker compose up -d selenium
```

5. **如果最新版本的镜像有问题，回退到稳定版本**
```bash
# 拉取稳定版本
docker pull selenium/standalone-chromium:147.0

# 修改 docker-compose.yml 中的镜像版本
# image: selenium/standalone-chromium:147.0

# 重启容器
docker compose up -d selenium
```

**常见镜像问题：**
- 镜像拉取失败：检查网络连接，尝试使用国内镜像源
- 容器启动失败：查看日志，可能是版本不兼容
- 容器反复重启：检查资源配置（内存、CPU）

### systemd 服务无法启动

```bash
# 检查服务状态
systemctl status weread-selenium.service

# 查看 systemd 日志
journalctl -u weread-selenium.service -f

# 检查服务是否启用
systemctl is-enabled weread-selenium.service

# 如果服务显示 disabled，执行启用
systemctl enable weread-selenium.service

# 如果存在 /etc/init.d/weread-selenium（OpenWrt 格式），应删除
rm -f /etc/init.d/weread-selenium

# 重新加载 systemd 配置
systemctl daemon-reload

# 重新启动服务
systemctl start weread-selenium.service
```

**常见错误：**
- `update-rc.d: error: weread-selenium Default-Start contains no runlevels` - 说明存在 OpenWrt 格式的 SysV 脚本，需要删除
- 服务显示 `disabled` - 执行 `systemctl enable weread-selenium.service`
- 服务显示 `activating (start-pre)` - 正在执行 180 秒等待，属正常现象

### 定时任务未执行

```bash
# 检查 crontab
crontab -l | grep weread-multi

# 检查系统时间
date

# 检查 cron 服务状态
ps aux | grep cron
```

### 数据清理验证

```bash
# 查看清理任务是否存在
crontab -l | grep "daily cleanup"

# 手动执行清理命令（测试用）
cd /vol1/docker/mycontainers/weread-challenge-selenium-muti-user
find data -name 'screenshot-*.png' -delete
find data -name 'output.log' -delete

# 查看清理后的数据目录
ls -la data/*/screenshot-*.png 2>/dev/null | wc -l  # 应为 0
ls -la data/*/login.png  # 应保留
```

### VNC 无法访问

```bash
netstat -tlnp | grep 7900
```

## 技术架构

```
               Selenium
          (端口 4444, VNC: 7900)
                 |
    +------+------+------+------+
    |      |      |      |      |
  app-1  app-2  app-3  app-4
  liujl  liujl   jpx    jpx
  4735   3016    155    181
```

## 部署信息

- **主机**：192.168.123.54
- **工作目录**：/vol1/docker/mycontainers/weread-challenge-selenium-muti-user
- **VNC 地址**：http://192.168.123.54:7900
- **阅读时长**：68分钟/次
- **每日次数**：4次
- **容器名称前缀**：weread-challenge-selenium-muti-user

## 关联文档

- [RK3566 iStoreOS 多用户部署方案](../rk3566-muti-user-deploy/README.md) - 另一台主机的部署文档
