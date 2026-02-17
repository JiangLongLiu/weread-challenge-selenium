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

## 目标方案：docker-compose 多用户

```
┌─────────────────┐
│ selenium        │  ← 单例，network_mode: host
│ (端口 4444)     │     SE_NODE_MAX_SESSIONS=10
│ (支持多会话)     │
└────────┬────────┘
         │ host 网络 (127.0.0.1:4444)
    ┌────┴────┐
    │         │
┌───┴───┐ ┌───┴───┐
│app-1  │ │app-2  │  ← 多个 app 服务
│user1  │ │user2  │     独立 data 目录
└───────┘ └───────┘
```

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
  app-user1:
    image: jqknono/weread-challenge:v0.13.0
    network_mode: host
    environment:
      - WEREAD_REMOTE_BROWSER=http://127.0.0.1:4444
      - WEREAD_USER=user1
    volumes:
      - ./data/user1:/app/data

  app-user2:
    image: jqknono/weread-challenge:v0.13.0
    network_mode: host
    environment:
      - WEREAD_REMOTE_BROWSER=http://127.0.0.1:4444
      - WEREAD_USER=user2
    volumes:
      - ./data/user2:/app/data
```

### 3. 定时任务

多用户场景下，需要为每个用户配置独立的定时任务：

```bash
# user1: 每 6 小时执行
0 */6 * * * cd /path/to/weread-multi && docker compose up app-user1 -d

# user2: 每 6 小时执行（错开 30 分钟避免资源竞争）
30 */6 * * * cd /path/to/weread-multi && docker compose up app-user2 -d
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

建议使用 `users.yml` 配置文件：

```yaml
users:
  - name: user1
    duration: 68
    cron_offset: 0      # 整点执行
  - name: user2
    duration: 68
    cron_offset: 30     # 偏移 30 分钟
```

## 注意事项

1. **资源限制**：RK3566 内存有限（通常 4GB），建议同时运行不超过 3 个用户
2. **会话隔离**：Selenium 多会话需要配置 `SE_NODE_MAX_SESSIONS`
3. **定时任务错开**：避免多个用户同时启动造成资源峰值
4. **VNC 访问**：多用户共用一个 VNC 端口（7900），需协调使用

## 待确认事项

- [ ] 目标用户数量？
- [ ] 每个用户的阅读时长？
- [ ] 是否需要独立的 VNC 端口？
- [ ] 远程主机 IP 和部署路径？