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
│liujl4735  │ │liujl3016 │  ← 独立容器，独立 data 目录
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
│liujl4735 ││liujl3016 ││jpx155 ││jpx181 │
└──────┘└──────┘└──────┘└──────┘
```

**分时执行：**
- 第1轮：00:00 - 04:40
- 第2轮：06:00 - 10:40
- 第3轮：13:00 - 17:40
- 第4轮：19:00 - 23:40

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
    - SE_NODE_DISPLAY_NAME="WeRead-MultiUser"  # VNC页面标题
```

### 2. 多 App 服务

```yaml
services:
  app-1:
    image: jqknono/weread-challenge:v0.13.0
    network_mode: host
    environment:
      - WEREAD_REMOTE_BROWSER=http://127.0.0.1:4444
      - WEREAD_USER=liujl4735
      - WEREAD_DURATION=68
    volumes:
      - ./data/liujl4735:/app/data

  app-2:
    image: jqknono/weread-challenge:v0.13.0
    network_mode: host
    environment:
      - WEREAD_REMOTE_BROWSER=http://127.0.0.1:4444
      - WEREAD_USER=liujl3016
      - WEREAD_DURATION=68
    volumes:
      - ./data/liujl3016:/app/data

  app-3:
    image: jqknono/weread-challenge:v0.13.0
    network_mode: host
    environment:
      - WEREAD_REMOTE_BROWSER=http://127.0.0.1:4444
      - WEREAD_USER=jpx155
      - WEREAD_DURATION=68
    volumes:
      - ./data/jpx155:/app/data

  app-4:
    image: jqknono/weread-challenge:v0.13.0
    network_mode: host
    environment:
      - WEREAD_REMOTE_BROWSER=http://127.0.0.1:4444
      - WEREAD_USER=jpx181
      - WEREAD_DURATION=68
    volumes:
      - ./data/jpx181:/app/data
```

### 3. 定时任务

多用户场景下，需要为每个用户配置独立的定时任务（每日4轮）：

```bash
# liujl4735: 00:00, 06:00, 13:00, 19:00
# liujl3016: 01:10, 07:10, 14:10, 20:10
# jpx155: 02:20, 08:20, 15:20, 21:20
# jpx181: 03:30, 09:30, 16:30, 22:30
```

## 执行记录

### 2024-XX-XX 部署完成

**执行步骤：**
1. ✓ 读取 password.xls 获取 SSH 凭据（192.168.123.51:22, root）
2. ✓ 创建 docker-compose.yml（4用户：liujl4735, liujl3016, jpx155, jpx181）
3. ✓ 创建 ssh_scp_util.py（无人值守部署脚本）
4. ✓ 创建 check-status.py（无人值守状态检查脚本）
5. ✓ 执行远程部署（上传配置、创建目录、配置16个定时任务）
6. ✓ 验证部署结果（数据目录已创建，定时任务已配置）

**经验总结：**
- 无人值守部署：通过 pandas 读取 Excel 密码，paramiko 实现 SSH 免交互
- 定时任务管理：每个用户4个任务，共16个，通过 crontab 统一管理
- 用户识别：VNC 页面通过 SE_NODE_DISPLAY_NAME 显示节点信息

**部署路径：** `/mnt/sata1-1/docker/mycontainers/weread-challenge-selenium-muti-user`

**VNC 地址：** http://192.168.123.51:7900

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
  - name: liujl4735
    duration: 68
    cron_times: ["0 0 * * *", "0 6 * * *", "0 13 * * *", "0 19 * * *"]
  - name: liujl3016
    duration: 68
    cron_times: ["10 1 * * *", "10 7 * * *", "10 14 * * *", "10 20 * * *"]
  - name: jpx155
    duration: 68
    cron_times: ["20 2 * * *", "20 8 * * *", "20 15 * * *", "20 21 * * *"]
  - name: jpx181
    duration: 68
    cron_times: ["30 3 * * *", "30 9 * * *", "30 16 * * *", "30 22 * * *"]
```

## 注意事项

1. **资源限制**：RK3566 内存有限（通常 4GB），4用户分时复用可稳定运行
2. **会话隔离**：Selenium 多会话需要配置 `SE_NODE_MAX_SESSIONS`
3. **定时任务错开**：每个用户间隔70分钟，避免资源竞争
4. **VNC 访问**：多用户共用一个 VNC 端口（7900），需按时间窗口登录
5. **登录窗口**：每个用户有5分钟登录时间，需配合扫码
6. **用户识别**：VNC 页面标题通过 `SE_NODE_DISPLAY_NAME` 显示当前会话信息，便于识别用户

## 待确认事项

- [x] 目标用户数量：**4个**
- [x] 每个用户的阅读时长：**68分钟**
- [x] 是否需要独立的 VNC 端口：**分时复用单 VNC**
- [x] 远程主机 IP 和部署路径：**192.168.123.51** / **/mnt/sata1-1/docker/mycontainers/weread-challenge-selenium-muti-user**
- [x] 每日阅读次数：**4次**

## 时间表设计

### 计算分析

```
用户间隔：70分钟（68分钟阅读 + 2分钟缓冲）
单轮时长：4用户 × 70分钟 = 280分钟 = 4小时40分钟
每日4轮：00:00, 06:00, 13:00, 19:00 起点
```

### 详细时间表

| 轮次 | liujl4735 | liujl3016 | jpx155 | jpx181 |
|------|------------|------------|---------|---------|
| 第1轮 | 00:00 | 01:10 | 02:20 | 03:30 |
| 第2轮 | 06:00 | 07:10 | 08:20 | 09:30 |
| 第3轮 | 13:00 | 14:10 | 15:20 | 16:30 |
| 第4轮 | 19:00 | 20:10 | 21:20 | 22:30 |

## 定时任务配置

```bash
# liujl4735: 00:00, 06:00, 13:00, 19:00
0 0 * * *  cd /path && docker compose up app-1 -d
0 6 * * *  cd /path && docker compose up app-1 -d
0 13 * * * cd /path && docker compose up app-1 -d
0 19 * * * cd /path && docker compose up app-1 -d

# liujl3016: 01:10, 07:10, 14:10, 20:10
10 1 * * *  cd /path && docker compose up app-2 -d
10 7 * * *  cd /path && docker compose up app-2 -d
10 14 * * * cd /path && docker compose up app-2 -d
10 20 * * * cd /path && docker compose up app-2 -d

# jpx155: 02:20, 08:20, 15:20, 21:20
20 2 * * *  cd /path && docker compose up app-3 -d
20 8 * * *  cd /path && docker compose up app-3 -d
20 15 * * * cd /path && docker compose up app-3 -d
20 21 * * * cd /path && docker compose up app-3 -d

# jpx181: 03:30, 09:30, 16:30, 22:30
30 3 * * *  cd /path && docker compose up app-4 -d
30 9 * * *  cd /path && docker compose up app-4 -d
30 16 * * * cd /path && docker compose up app-4 -d
30 22 * * * cd /path && docker compose up app-4 -d
```