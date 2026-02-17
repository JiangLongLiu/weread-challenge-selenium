# RK3566 多用户部署分析与计划

## 背景

在 RK3566 iStoreOS 主机上部署微信读书助手，支持多个用户独立阅读。

## 现有方案对比

### 方案 A：README.md 原始方案（docker run）

```
┌─────────────────┐
│ selenium-live   │  ← 单例，端口 4444, 7900
│ (共享浏览器)     │
└────────┬────────┘
         │ weread-challenge-net
    ┌────┴────┐
    │         │
┌───┴───┐ ┌───┴───┐
│user1  │ │user2  │  ← 独立容器，独立 data 目录
│docker │ │docker │
│run    │ │run    │
└───────┘ └───────┘
```

**特点：**
- 使用 `docker run` 命令启动
- 共享 selenium 容器（支持多会话）
- 每个用户独立 data 目录
- 通过 crontab 管理定时任务

### 方案 B：rk3566-istoreos-deploy 单用户方案（docker-compose）

```
┌─────────────────┐
│ selenium        │  ← network_mode: host
│ (端口 4444)     │
└────────┬────────┘
         │ host 网络
┌────────┴────────┐
│ app             │  ← 单用户
│ (data 目录)     │
└─────────────────┘
```

**特点：**
- 使用 docker-compose.yml 编排
- network_mode: host
- 每 6 小时执行一次
- 通过 SSH 远程部署

## 目标方案：docker-compose 多用户（4用户分时复用）

```
┌─────────────────┐
│ selenium        │  ← 单例，network_mode: host
│ (端口 4444)     │     SE_NODE_MAX_SESSIONS=10
│ (支持多会话)     │     VNC: 7900
└────────┬────────┘
         │ host 网络 (127.0.0.1:4444)
    ┌────┼────┬────┐
    │    │    │    │
┌───┴──┐┌──┴───┐┌──┴───┐┌──┴───┐
│app-1 ││app-2 ││app-3 ││app-4 │
│user1 ││user2 ││user3 ││user4 │
└──────┘└──────┘└──────┘└──────┘
```

**分时执行：**
- 第一轮：00:00 - 04:40
- 第二轮：12:00 - 16:40

## 技术要点

### 1. Selenium 单例多会话

```yaml
selenium:
  image: selenium/standalone-chromium:144.0
  network_mode: host
  environment:
    - SE_NODE_MAX_INSTANCES=10    # 最大实例数
    - SE_NODE_MAX_SESSIONS=10     # 最大并发会话
    - SE_NODE_OVERRIDE_MAX_SESSIONS=true
```

### 2. 多 App 服务

```yaml
services:
  app-1:
    image: jqknono/weread-challenge:v0.13.0
    network_mode: host
    environment:
      - WEREAD_REMOTE_BROWSER=http://127.0.0.1:4444
      - WEREAD_USER=user1
      - WEREAD_DURATION=68
    volumes:
      - ./data/user1:/app/data

  app-2:
    image: jqknono/weread-challenge:v0.13.0
    network_mode: host
    environment:
      - WEREAD_REMOTE_BROWSER=http://127.0.0.1:4444
      - WEREAD_USER=user2
      - WEREAD_DURATION=68
    volumes:
      - ./data/user2:/app/data

  app-3:
    image: jqknono/weread-challenge:v0.13.0
    network_mode: host
    environment:
      - WEREAD_REMOTE_BROWSER=http://127.0.0.1:4444
      - WEREAD_USER=user3
      - WEREAD_DURATION=68
    volumes:
      - ./data/user3:/app/data

  app-4:
    image: jqknono/weread-challenge:v0.13.0
    network_mode: host
    environment:
      - WEREAD_REMOTE_BROWSER=http://127.0.0.1:4444
      - WEREAD_USER=user4
      - WEREAD_DURATION=68
    volumes:
      - ./data/user4:/app/data
```

### 3. 定时任务

多用户场景下，需要为每个用户配置独立的定时任务（每日2轮）：

```bash
# 第一轮 (00:00 - 04:40)
0 0 * * *  cd /path && docker compose up app-1 -d   # user1 @ 00:00
10 1 * * * cd /path && docker compose up app-2 -d   # user2 @ 01:10
20 2 * * * cd /path && docker compose up app-3 -d   # user3 @ 02:20
30 3 * * * cd /path && docker compose up app-4 -d   # user4 @ 03:30

# 第二轮 (12:00 - 16:40)
0 12 * * *  cd /path && docker compose up app-1 -d  # user1 @ 12:00
10 13 * * * cd /path && docker compose up app-2 -d  # user2 @ 13:10
20 14 * * * cd /path && docker compose up app-3 -d  # user3 @ 14:20
30 15 * * * cd /path && docker compose up app-4 -d  # user4 @ 15:30
```

## 实现计划

### 阶段 1：基础结构搭建

1. 创建目录结构
   ```
   rk3566-muti-user-deploy/
   ├── docker-compose.yml      # 多用户编排
   ├── scripts/
   │   ├── ssh_scp_util.py    # 远程部署脚本
   │   ├── setup-cron.sh      # 定时任务配置
   │   └── check-status.py    # 状态检查
   ├── password.xls            # SSH 密码
   └── README.md               # 使用说明
   ```

2. 编写 docker-compose.yml
   - selenium 服务（单例，支持多会话）
   - 多个 app 服务（按需添加用户）

3. 适配 setup-cron.sh
   - 为每个用户配置独立定时任务
   - 错开执行时间避免资源竞争

### 阶段 2：部署脚本适配

1. 修改 ssh_scp_util.py
   - 支持多用户配置
   - 自动创建用户 data 目录

2. 修改 check-status.py
   - 检查所有用户容器状态
   - 检查各用户定时任务

### 阶段 3：文档与测试

1. 编写 README.md
2. 编写快速开始指南
3. 实际部署测试

## 用户配置文件设计

使用 `users.yml` 配置文件：

```yaml
users:
  - name: user1
    duration: 68
    cron_round1: "0 0 * * *"   # 00:00
    cron_round2: "0 12 * * *"  # 12:00
  - name: user2
    duration: 68
    cron_round1: "10 1 * * *"  # 01:10
    cron_round2: "10 13 * * *" # 13:10
  - name: user3
    duration: 68
    cron_round1: "20 2 * * *"  # 02:20
    cron_round2: "20 14 * * *" # 14:20
  - name: user4
    duration: 68
    cron_round1: "30 3 * * *"  # 03:30
    cron_round2: "30 15 * * *" # 15:30
```

## 注意事项

1. **资源限制**：RK3566 内存有限（通常 4GB），4用户分时复用可稳定运行
2. **会话隔离**：Selenium 多会话需要配置 `SE_NODE_MAX_SESSIONS`
3. **定时任务错开**：每个用户间隔70分钟，避免资源竞争
4. **VNC 访问**：多用户共用一个 VNC 端口（7900），需按时间窗口登录
5. **登录窗口**：每个用户有5分钟登录时间，需配合扫码

## 待确认事项

- [x] 目标用户数量：**4个**
- [x] 每个用户的阅读时长：**68分钟**
- [x] 是否需要独立的 VNC 端口：**分时复用单 VNC**
- [x] 远程主机 IP 和部署路径：**192.168.123.51** / **/mnt/sata1-1/docker/mycontainers/weread-challenge-selenium-muti-user**
- [x] 每日阅读次数：**2次**

## 时间表设计

### 计算分析

```
单轮时长 = 68分钟阅读 + 2分钟缓冲 = 70分钟
4用户单轮 = 70 × 4 = 280分钟 = 4.7小时
每日2轮 = 9.4小时（时间充裕）
```

### 第一轮 (00:00 - 04:40)

| 用户 | 开始时间 | 结束时间 | VNC 登录窗口 |
|------|----------|----------|--------------|
| user1 | 00:00 | 01:08 | 00:00-00:05 |
| user2 | 01:10 | 02:18 | 01:10-01:15 |
| user3 | 02:20 | 03:28 | 02:20-02:25 |
| user4 | 03:30 | 04:38 | 03:30-03:35 |

### 第二轮 (12:00 - 16:40)

| 用户 | 开始时间 | 结束时间 |
|------|----------|----------|
| user1 | 12:00 | 13:08 |
| user2 | 13:10 | 14:18 |
| user3 | 14:20 | 15:28 |
| user4 | 15:30 | 16:38 |

## 定时任务配置

```bash
# 第一轮
0 0 * * *  cd /path && docker compose up app-1 -d   # user1 @ 00:00
10 1 * * * cd /path && docker compose up app-2 -d   # user2 @ 01:10
20 2 * * * cd /path && docker compose up app-3 -d   # user3 @ 02:20
30 3 * * * cd /path && docker compose up app-4 -d   # user4 @ 03:30

# 第二轮
0 12 * * *  cd /path && docker compose up app-1 -d  # user1 @ 12:00
10 13 * * * cd /path && docker compose up app-2 -d  # user2 @ 13:10
20 14 * * * cd /path && docker compose up app-3 -d  # user3 @ 14:20
30 15 * * * cd /path && docker compose up app-4 -d  # user4 @ 15:30
```