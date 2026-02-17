# account-3016 本地部署配置

Windows 本地 Docker 部署配置，用于微信读书自动阅读。

## 文件结构

```
account-3016/
├── docker-compose.yml    # Docker 容器编排配置
├── scripts/
│   ├── deploy.py         # 一键部署脚本
│   ├── setup-task.ps1   # Windows 定时任务配置脚本
│   └── remove-task.ps1  # 删除定时任务脚本
├── 定时任务.md            # 定时任务配置说明
├── 快速开始.md            # 快速使用指南
└── README.md             # 本文件
```

## 快速开始

### 1. 运行部署

```bash
python docs/docker-windows-build/account-3016/scripts/deploy.py
```

### 2. 配置定时任务（可选）
部署后会将 docker-compose.yml 复制到工作目录。配置定时任务需要：
1. 以管理员身份运行 PowerShell
2. 执行：`powershell -ExecutionPolicy Bypass -File scripts/setup-task.ps1`

详见 [定时任务.md](./定时任务.md)

### 2. 访问 VNC 扫码登录

- VNC 界面: http://localhost:7900
- VNC 密码: 111111

详见 [快速开始.md](./快速开始.md)

## 配置说明

### docker-compose.yml

定义两个服务：

| 服务 | 说明 |
|------|------|
| `app` | 微信读书阅读脚本 |
| `selenium` | Chrome 浏览器 (VNC + Grid) |

关键配置：
- 镜像: `jqknono/weread-challenge:v0.13.0`
- 端口: 4444 (Selenium Grid), 7900 (VNC)
- DNS: 223.5.5.5 (阿里 DNS)
- VNC 密码: 111111
- 阅读时长: 68 分钟

### deploy.py

自动化部署脚本，执行以下步骤：

1. 创建工作目录 `E:\dockers\weread-challenge-selenium-3016`
2. 强制覆盖 docker-compose.yml
3. 删除旧容器
4. 启动容器

### 定时任务
部署后可以配置 Windows 任务计划程序，实现每 6 小时自动阅读。详见 [定时任务.md](./定时任务.md)

## 常用命令

```bash
# 查看容器状态
docker ps | grep weread-challenge-selenium-3016

# 查看日志
docker logs -f weread-challenge-selenium-3016-app-1

# 停止容器
docker compose -f E:\dockers\weread-challenge-selenium-3016\docker-compose.yml down

# 重新部署
python docs/docker-windows-build/account-3016/scripts/deploy.py
```

## 注意事项

- Windows 下使用桥接模式 + 端口映射
- 容器间通信使用服务名 `selenium:4444`
- 端口 4444、7900 不能被占用
