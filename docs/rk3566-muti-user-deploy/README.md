# RK3566 4用户微信读书助手部署

4用户分时复用部署方案，支持 liujl4735、liujl3016、jpx155、jpx181 四个账号独立阅读。

## 快速开始

### 1. 部署

```bash
python docs/rk3566-muti-user-deploy/scripts/ssh_scp_util.py
```

自动完成：
- 读取 password.xls 中的 SSH 凭据
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

> 提示：每个用户有5分钟登录窗口，请在对应时间点前后登录扫码。

## 文件结构

```
rk3566-muti-user-deploy/
├── docker-compose.yml          # 容器编排配置
├── password.xls                # SSH 凭据（不提交Git）
├── PLAN.md                     # 部署计划与执行记录
├── README.md                   # 本文件
├── 会话清理问题分析.md          # Selenium 会话清理方案
└── scripts/
    ├── ssh_scp_util.py        # 部署脚本
    ├── check-status.py        # 状态检查脚本
    └── weread-selenium.init   # 开机启动脚本模板
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

## 注意事项

1. **VNC 共享**：4用户共用一个 VNC 端口，需按时间窗口错开使用
2. **首次登录**：每个账号首次需手动扫码，后续自动保持登录状态
3. **阅读时长**：每次阅读68分钟，每日4次
4. **定时任务**：由 crontab 管理，可通过 `crontab -l` 查看
5. **会话清理**：定时任务自动重启 Selenium 容器清理浏览器会话，详见[会话清理问题分析.md](会话清理问题分析.md)

## 相关文档

- [PLAN.md](PLAN.md) - 部署计划、技术方案与执行记录
- [会话清理问题分析.md](会话清理问题分析.md) - Selenium 4.x 会话清理方案
- [scripts/ssh_scp_util.py](scripts/ssh_scp_util.py) - 自动化部署脚本
- [scripts/check-status.py](scripts/check-status.py) - 状态检查脚本
- [scripts/weread-selenium.init](scripts/weread-selenium.init) - 开机启动脚本模板

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
