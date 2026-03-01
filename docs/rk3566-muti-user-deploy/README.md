# RK3566 4用户微信读书助手部署

4用户分时复用部署方案，支持 liujl4735、liujl3016、jpx155、jpx181 四个账号独立阅读。

## 快速开始

### 1. 部署

```bash
python docs/rk3566-muti-user-deploy/scripts/ssh_scp_util.py
```

自动完成：
- 读取 password.csv 中的 SSH 凭据
- 上传 docker-compose.yml 到远程主机
- 创建4个用户的数据目录
- 配置16个定时任务（每用户4个）

### 2. 检查状态

```bash
python docs/rk3566-muti-user-deploy/scripts/check-status.py
```

### 3. 首次登录

访问 VNC 界面扫码登录：
- 地址：http://192.168.123.51:7900
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
rk3566-muti-user-deploy/
├── docker-compose.yml          # 容器编排配置
├── password.csv                # SSH 凭据（不提交Git）
├── PLAN.md                     # 部署计划与执行记录
├── README.md                   # 本文件
├── 会话清理问题分析.md          # Selenium 会话清理方案
└── scripts/
    ├── ssh_scp_util.py        # 部署脚本（含开机启动配置）
    ├── check-status.py        # 状态检查脚本
    ├── weread-selenium.init   # 开机启动脚本模板
    ├── check_time_and_tasks.py  # 检查时间和定时任务
    ├── debug_app1.py          # 调试 app-1 启动
    ├── pull_image.py          # 拉取 Docker 镜像
    ├── check_vnc.py           # 检查 VNC 服务状态
    ├── check_vnc_detail.py    # VNC 详细诊断
    ├── check_xvfb.py          # 检查 Xvfb 启动问题
    ├── check_xvfb_error.py    # 检查 Xvfb 错误日志
    ├── check_xvfb_logs.py     # 检查 Xvfb 日志文件
    ├── test_xvfb.py           # 测试 Xvfb 启动
    ├── test_xvfb_manual.py    # 手动测试 Xvfb 启动
    ├── test_xvfb_simple.py    # 简化测试 Xvfb 启动
    └── check_boot_log.py      # 检查开机启动日志
```

### 远程主机（RK3566）文件

```
/etc/init.d/weread-selenium              # 开机启动脚本（由 ssh_scp_util.py 创建）
/etc/rc.d/S99weread-selenium             # 开机链接（指向 init.d 脚本）
/var/spool/cron/crontabs/root            # 定时任务存储
/mnt/sata1-1/docker/mycontainers/        # Docker 工作目录
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
cd /mnt/sata1-1/docker/mycontainers/weread-challenge-selenium-muti-user && docker compose up -d selenium

# liujl4735
cd /mnt/sata1-1/docker/mycontainers/weread-challenge-selenium-muti-user && docker compose up app-1 -d

# liujl3016
cd /mnt/sata1-1/docker/mycontainers/weread-challenge-selenium-muti-user &&  docker compose up app-2 -d

# jpx155
cd /mnt/sata1-1/docker/mycontainers/weread-challenge-selenium-muti-user &&  docker compose up app-3 -d

# jpx181
cd /mnt/sata1-1/docker/mycontainers/weread-challenge-selenium-muti-user &&  docker compose up app-4 -d
```

### 手动停止阅读

```bash
# selenium
cd /mnt/sata1-1/docker/mycontainers/weread-challenge-selenium-muti-user && docker compose stop selenium

# liujl4735
cd /mnt/sata1-1/docker/mycontainers/weread-challenge-selenium-muti-user &&  docker compose stop app-1
# 模拟定时任务的停止流程（关键测试）
cd /mnt/sata1-1/docker/mycontainers/weread-challenge-selenium-muti-user && docker compose stop app-1 && docker restart weread-challenge-selenium-muti-user-selenium-1

# liujl3016
cd /mnt/sata1-1/docker/mycontainers/weread-challenge-selenium-muti-user &&  docker compose stop app-2

# jpx155
cd /mnt/sata1-1/docker/mycontainers/weread-challenge-selenium-muti-user && docker compose stop app-3

# jpx181
cd /mnt/sata1-1/docker/mycontainers/weread-challenge-selenium-muti-user &&  docker compose stop app-4
```

### 查看日志

```bash
cd /mnt/sata1-1/docker/mycontainers/weread-challenge-selenium-muti-user
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
python docs/rk3566-muti-user-deploy/scripts/ssh_scp_util.py
```

### 管理开机启动

在 RK3566 上手动管理 Selenium 开机启动：

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
   - 定义文件：`scripts/ssh_scp_util.py` 第 177-216 行
   - 防重复机制：部署时自动清理旧任务（过滤关键词：`weread`、`selenium-muti-user`、`account-4735`）

5. **会话清理**：定时任务自动重启 Selenium 容器清理浏览器会话，详见[会话清理问题分析.md](会话清理问题分析.md)

6. **数据清理**：每日 23:59 自动清理所有用户的截图（screenshot-*.png）和日志（output.log），保留 login.png
   - 清理范围：`data/*/screenshot-*.png`、`data/*/output.log`
   - 持久化机制：清理任务与其他定时任务一样存储在 `/var/spool/cron/crontabs/root`，RK3566 重启后依然有效
   - 验证方法：`crontab -l | grep "daily cleanup"`

## 相关文档

- [PLAN.md](PLAN.md) - 部署计划、技术方案与执行记录
- [会话清理问题分析.md](会话清理问题分析.md) - Selenium 4.x 会话清理方案
- [scripts/ssh_scp_util.py](scripts/ssh_scp_util.py) - 自动化部署脚本
- [scripts/check-status.py](scripts/check-status.py) - 状态检查脚本
- [scripts/weread-selenium.init](scripts/weread-selenium.init) - 开机启动脚本模板
- [scripts/check_time_and_tasks.py](scripts/check_time_and_tasks.py) - 检查时间和定时任务
- [scripts/debug_app1.py](scripts/debug_app1.py) - 调试 app-1 启动
- [scripts/pull_image.py](scripts/pull_image.py) - 拉取 Docker 镜像

### VNC 故障排查脚本

- [scripts/check_vnc.py](scripts/check_vnc.py) - 检查 VNC 服务状态
- [scripts/check_vnc_detail.py](scripts/check_vnc_detail.py) - VNC 详细诊断
- [scripts/check_xvfb.py](scripts/check_xvfb.py) - 检查 Xvfb 启动问题
- [scripts/check_xvfb_error.py](scripts/check_xvfb_error.py) - 检查 Xvfb 错误日志
- [scripts/check_xvfb_logs.py](scripts/check_xvfb_logs.py) - 检查 Xvfb 日志文件
- [scripts/test_xvfb.py](scripts/test_xvfb.py) - 测试 Xvfb 启动
- [scripts/test_xvfb_manual.py](scripts/test_xvfb_manual.py) - 手动测试 Xvfb 启动
- [scripts/test_xvfb_simple.py](scripts/test_xvfb_simple.py) - 简化测试 Xvfb 启动
- [scripts/check_boot_log.py](scripts/check_boot_log.py) - 检查开机启动日志

## 开机启动流程

RK3566 重启后，Selenium 容器通过 OpenWrt 启动脚本自动启动：

```
RK3566 重启
    ↓
OpenWrt 启动完成
    ↓
/etc/rc.d/S99weread-selenium 执行（START=99，最后启动）
    ↓
echo "Waiting 180 seconds for system to stabilize..."
    ↓
sleep 180（等待3分钟，避免CPU卡死）
    ↓
while 循环等待 Docker 就绪
    ↓
docker compose up -d selenium 启动
    ↓
Selenium 运行（restart: unless-stopped 保证异常时重启）
```

### 启动脚本位置

- **脚本文件**: `/etc/init.d/weread-selenium`
- **开机链接**: `/etc/rc.d/S99weread-selenium`
- **定义来源**: `scripts/ssh_scp_util.py` 第 129-172 行

### 启动延迟说明

- **延迟时间**: 180 秒（3分钟）
- **原因**: RK3566 性能有限，避免开机时 CPU 卡死
- **配置位置**: `ssh_scp_util.py` 中 `start()` 函数的 `sleep 180`

### X11 清理功能（关键）

开机启动脚本会自动清理旧的 X11 资源，避免 VNC/Xvfb 启动失败：

```bash
# 清理旧的 X11 socket 和锁文件，避免显示号冲突
rm -f /tmp/.X*-lock /tmp/.X11-unix/X* 2>/dev/null
echo "Cleaned up old X11 resources"
```

**为什么需要清理**：
- 主机重启后，X11 socket 可能残留，占用显示号
- 旧容器未正常关闭时，锁文件会阻止新容器启动
- 之前使用 :99 显示号会冲突，现改为 :98

**验证方法**：
```bash
python docs/rk3566-muti-user-deploy/scripts/check_boot_log.py
```

日志中应显示：`Cleaned up old X11 resources`

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
docker restart weread-challenge-selenium-muti-user-selenium-1
```

### 数据清理任务

```bash
# 每日 23:59 执行
cd /mnt/sata1-1/docker/mycontainers/weread-challenge-selenium-muti-user
find data -name 'screenshot-*.png' -delete
find data -name 'output.log' -delete
```

## 故障排查

### 容器无法启动

```bash
# 检查 Selenium 健康状态
docker ps | grep selenium

# 查看详细日志
docker compose logs selenium
```

### 定时任务未执行

```bash
# 检查 crontab
crontab -l | grep weread-multi

# 检查系统时间
date
```

### 数据清理验证

```bash
# 查看清理任务是否存在
crontab -l | grep "daily cleanup"

# 手动执行清理命令（测试用）
cd /mnt/sata1-1/docker/mycontainers/weread-challenge-selenium-muti-user
find data -name 'screenshot-*.png' -delete
find data -name 'output.log' -delete

# 查看清理后的数据目录
ls -la data/*/screenshot-*.png 2>/dev/null | wc -l  # 应为 0
ls -la data/*/login.png  # 应保留
```

### VNC 无法访问

```bash
# 检查端口监听
netstat -tlnp | grep 7900
```

## 技术架构

```
┌─────────────────┐
│   Selenium      │  ← 单例，多会话支持
│  (端口 4444)    │
│  VNC: 7900      │
└────────┬────────┘
         │
    ┌────┼────┬────┐
    │    │    │    │
┌───┴──┐┌──┴───┐┌──┴───┐┌──┴───┐
│app-1 ││app-2 ││app-3 ││app-4 │
│liujl ││liujl ││jpx   ││jpx   │
│4735  ││3016  ││155   ││181   │
└──────┘└──────┘└──────┘└──────┘
```

## 部署信息

- **主机**：192.168.123.51
- **工作目录**：/mnt/sata1-1/docker/mycontainers/weread-challenge-selenium-muti-user
- **VNC 地址**：http://192.168.123.51:7900
- **阅读时长**：68分钟/次
- **每日次数**：4次
