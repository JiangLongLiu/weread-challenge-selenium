# RK3566-OECT1-2-fnOS 4用户微信读书助手部署

4用户分时复用部署方案，支持 liujl4735、liujl3016、jpx155、jpx181 四个账号独立阅读。

## 快速开始

### 1. 部署

```bash
python docs/rk3566-oect1-2-fnOS-deploy/scripts/ssh_scp_util.py
```

### 2. 检查状态

```bash
python docs/rk3566-oect1-2-fnOS-deploy/scripts/check-status.py
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

## 文件结构

```
rk3566-oect1-2-fnOS-deploy/
├── docker-compose.yml
├── password.csv
├── README.md
└── scripts/
    ├── ssh_scp_util.py
    ├── check-status.py
    ├── start_selenium.py
    ├── 调试/
    └── 工具/
```

## 部署信息

- 主机：192.168.123.52
- 工作目录：/vol1/docker/mycontainers/weread-challenge-selenium-muti-user
- VNC 地址：http://192.168.123.52:7900
- 容器名称前缀：selenium-weread-challenge-selenium-oect1

## 关联文档

- [RK3566 iStoreOS 多用户部署方案](../rk3566-muti-user-deploy/README.md)
