# RK3566-OECT-2-fnOS 4用户微信读书助手部署

4用户分时复用部署方案，支持 liujl4735、liujl3016、jpx155、jpx181 四个账号独立阅读。

部署于 RK3566-OECT-2-fnOS 主机。

## 快速开始

### 1. 部署

```bash
python docs/rk3566-oect-2-fnOS-deploy/scripts/ssh_scp_util.py
```

自动完成：
- 读取 password.csv 中的 SSH 凭据
- 上传 docker-compose.yml 到远程主机
- 创建4个用户的数据目录
- 配置16个定时任务（4用户×4时段）

### 2. 检查状态

```bash
python docs/rk3566-oect-2-fnOS-deploy/scripts/check-status.py
```

### 3. 首次登录

访问 VNC 界面扫码登录：
- 地址：http://192.168.123.52:7900
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
rk3566-oect-2-fnOS-deploy/
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

### 远程主机（RK3566-OECT-2-fnOS）文件

```
/etc/init.d/weread-selenium              # 开机启动脚本（由 ssh_scp_util.py 创建）
/etc/rc.d/S99weread-selenium             # 开机链接（指向 init.d 脚本）
/var/spool/cron/crontabs/root            # 定时任务存储
/vol1/docker/mycontainers/               # Docker 工作目录
└── weread-challenge-selenium-muti-user/
    ├── docker-compose.yml
    └── data/
        ├── liujl4735/
        ├── liujl3016/
        ├── jpx155/
        └── jpx181/
```

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
python docs/rk3566-oect-2-fnOS-deploy/scripts/ssh_scp_util.py
```

### 管理开机启动

```bash
# 查看开机启动脚本
cat /etc/init.d/weread-selenium

# 查看开机链接
ls -la /etc/rc.d/S99weread-selenium

# 手动启用开机启动
/etc/init.d/weread-selenium enable

# 手动禁用开机启动
/etc/init.d/weread-selenium disable

# 手动启动（带180秒延迟）
/etc/init.d/weread-selenium start

# 手动停止
/etc/init.d/weread-selenium stop

# 查看状态
/etc/init.d/weread-selenium status
```

## 注意事项

1. **VNC 共享**：4用户共用一个 VNC 端口，需按时间窗口错开使用
2. **首次登录**：每个账号首次需手动扫码，后续自动保持登录状态
3. **阅读时长**：每次阅读68分钟，每日4次
4. **定时任务**：由 crontab 管理，共 17 个任务（16 个阅读 + 1 个清理）
   - 存储位置：`/var/spool/cron/crontabs/root`
   - 防重复机制：部署时自动清理旧任务

5. **数据清理**：每日 23:59 自动清理所有用户的截图（screenshot-*.png）和日志（output.log），保留 login.png
   - 清理范围：`data/*/screenshot-*.png`、`data/*/output.log`
   - 持久化机制：清理任务与其他定时任务一样存储在 `/var/spool/cron/crontabs/root`，主机重启后依然有效
   - 验证方法：`crontab -l | grep "daily cleanup"`

## 相关文档

- [scripts/ssh_scp_util.py](scripts/ssh_scp_util.py) - 自动化部署脚本
- [scripts/check-status.py](scripts/check-status.py) - 状态检查脚本
- [scripts/start_selenium.py](scripts/start_selenium.py) - 手动启动 Selenium
- [scripts/weread-selenium.init](scripts/weread-selenium.init) - 开机启动脚本模板
- [scripts/工具/check_time_and_tasks.py](scripts/工具/check_time_and_tasks.py) - 检查时间和定时任务
- [scripts/调试/debug_app1.py](scripts/调试/debug_app1.py) - 调试 app-1 启动
- [scripts/工具/pull_image.py](scripts/工具/pull_image.py) - 拉取 Docker 镜像

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

RK3566-OECT-2-fnOS（Debian）重启后，通过 systemd 服务自动启动 Selenium 容器：

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

### X11 清理功能

```bash
rm -f /tmp/.X*-lock /tmp/.X11-unix/X* 2>/dev/null
```

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

- **主机**：192.168.123.52
- **工作目录**：/vol1/docker/mycontainers/weread-challenge-selenium-muti-user
- **VNC 地址**：http://192.168.123.52:7900
- **阅读时长**：68分钟/次
- **每日次数**：4次
- **容器名称前缀**：weread-challenge-selenium-muti-user

## 关联文档

- [RK3566 iStoreOS 多用户部署方案](../rk3566-muti-user-deploy/README.md) - 另一台主机的部署文档
