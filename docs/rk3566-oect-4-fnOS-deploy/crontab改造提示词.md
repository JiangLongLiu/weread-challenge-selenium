# RK3566-OECT-4-fnOS 微信读书容器调度改造 — 提示词文档

## 一、改造背景

当前 RK3566-OECT-4-fnOS 主机（192.168.1.54）上部署了微信读书多用户自动阅读服务，原配置存在以下问题：

1. **用户过多**：原有 4 个用户（liujl4735、liujl3016、jpx155、jpx181），其中 jpx155 和 jpx181 缺少 cookies.json，每次需扫码登录
2. **调度分散**：每个用户每天 4 个时间窗口（间隔约 6 小时），每次运行 70 分钟，Selenium 全天运行
3. **开机自启 Selenium**：通过 systemd `weread-selenium.service` 开机拉起，资源浪费严重
4. **服务器重启无恢复**：如果服务器在非预期时间重启，crontab 不会补执行错过的任务

## 二、改造目标

1. **精简用户**：仅保留 liujl4735（app-1）和 liujl3016（app-2）
2. **集中运行窗口**：每日 02:25 ~ 05:35（共 3 小时 10 分钟），其余时间 Selenium 不运行
3. **错峰执行**：app-1 和 app-2 顺序运行，不重叠；交接时三个动作（app-1 停止、Selenium 重启、app-2 启动）间隔 1 分钟，避免 RK3566 瞬时压力
4. **取消开机自启**：禁用 systemd `weread-selenium.service`，Selenium 仅通过 crontab 调度
5. **重启恢复**：新增 `@reboot` 规则，服务器重启时检测时间窗口，在窗口内则自动补启动

## 三、容器与用户映射关系

| 容器名 | compose 服务名 | 用户 | 镜像 |
|---|---|---|---|
| weread-challenge-selenium-muti-user | selenium | —（共享浏览器） | selenium/standalone-chromium:147.0 |
| app-1-1-weread-challenge-selenium-muti-user | app-1 | liujl4735 | jqknono/weread-challenge:v0.15.0 |
| app-2-1-weread-challenge-selenium-muti-user | app-2 | liujl3016 | jqknono/weread-challenge:v0.15.0 |

docker-compose 文件位置：`/vol1/docker/mycontainers/weread-challenge-selenium-muti-user/docker-compose.yml`

## 四、完整时间线

```
02:25         02:30                    04:00   04:01         04:02               05:30   05:35
  │              │                       │       │              │                   │       │
  ▼              ▼                       ▼       ▼              ▼                   ▼       ▼
Selenium启动  app-1启动              app-1停  Selenium重启  app-2启动           app-2停  Selenium停
(预热浏览器)  (liujl4735开始阅读)    (释放)   (清理会话)    (liujl3016开始阅读)  (释放)   (收尾)
```

### 4.1 各阶段详解

| 时间 | crontab 条目 | 动作 | 说明 |
|---|---|---|---|
| 02:25 | `25 2 * * *` | `docker compose up selenium -d` | 启动 Selenium 容器，预热 Chromium 浏览器，等待 healthcheck 通过 |
| 02:30 | `30 2 * * *` | `docker compose up app-1 -d` + 后台 sleep 5400 | 启动 app-1 容器开始阅读；后台进程 90 分钟后自动停止 app-1 |
| 04:00 | （后台 sleep 触发） | `docker compose stop app-1` | app-1 的 sleep 5400（90 分钟）到期，自动停止容器 |
| 04:01 | `1 4 * * *` | `docker restart weread-challenge-selenium-muti-user` | 重启 Selenium 容器，释放浏览器会话、清理残留进程 |
| 04:02 | `2 4 * * *` | `docker compose up app-2 -d` + 后台 sleep 5280 | 启动 app-2 容器开始阅读；后台进程 88 分钟后自动停止 app-2 |
| 05:30 | （后台 sleep 触发） | `docker compose stop app-2` | app-2 的 sleep 5280（88 分钟）到期，自动停止容器 |
| 05:35 | `35 5 * * *` | 停止所有 app + selenium | 兜底清理：确保所有容器停止，Selenium 关闭 |
| 23:59 | `59 23 * * *` | 删除 screenshot-*.png 和 output.log | 每日数据清理 |

### 4.2 为什么 app-2 的 sleep 是 5280 而不是 5400？

- app-2 在 04:02 启动，需要在 05:30 停止
- 05:30 - 04:02 = 88 分钟 = 5280 秒
- 这样 app-2 在 05:30 停止后，05:35 的全局清理只负责停止 Selenium，留有 5 分钟缓冲

### 4.3 为什么交接动作要间隔 1 分钟？

RK3566 是 ARM 设备，CPU 和内存资源有限。如果在 04:00 同时执行：
- 停止 app-1（释放内存、关闭浏览器会话）
- 重启 Selenium（重新初始化 Chromium、分配内存）
- 启动 app-2（新建浏览器连接）

三个动作叠加会造成瞬时 CPU 飙升和内存争抢。间隔 1 分钟让每个动作有充足时间完成资源回收后再启动下一个。

## 五、@reboot 重启恢复逻辑

### 5.1 问题场景

crontab 是时间触发型调度器，只在精确时间点触发一次。如果服务器在 02:25 之后重启（如 03:30 断电恢复），02:25 的 crontab 条目不会补执行，当天的阅读任务就会丢失。

### 5.2 解决方案

添加 `@reboot` 规则：服务器启动时自动检查当前时间是否落在 02:25~05:35 窗口内，如果是则补启动容器。

### 5.3 恢复逻辑详解

```bash
# 伪代码
H = 当前小时
M = 当前分钟
T = H * 60 + M   # 当前时刻转换为"从 00:00 起算的分钟数"

如果 145 ≤ T ≤ 335：          # 145 = 02:25, 335 = 05:35
    启动 selenium
    等待 30 秒                 # 给 Selenium 初始化时间
    如果 T < 240：             # 240 = 04:00，还在 app-1 时段
        启动 app-1
    否则如果 T ≥ 242：         # 242 = 04:02，已过 app-2 启动时间
        启动 app-2
    否则：                      # 240 ≤ T < 242，处于交接过渡期
        什么都不做              # 避免与 04:01/04:02 的 crontab 冲突
```

### 5.4 恢复时间范围表

| 重启时间范围 | T 值范围 | 恢复动作 | 理由 |
|---|---|---|---|
| 02:25 ~ 03:59 | 145 ~ 239 | selenium + app-1 | app-1 时段内，补启动两个容器 |
| 04:00 ~ 04:01 | 240 ~ 241 | 仅 selenium | 过渡期，避免与正在执行的 crontab 冲突 |
| 04:02 ~ 05:35 | 242 ~ 335 | selenium + app-2 | app-2 时段内，补启动两个容器 |
| 05:36 ~ 02:24 | 其他 | 什么都不做 | 非运行窗口，无需启动 |

## 六、具体执行步骤

### 步骤 1：禁用 systemd 开机自启

在远程主机上执行：

```bash
systemctl disable weread-selenium.service
systemctl stop weread-selenium.service
```

通过 SSH 工具执行：

```powershell
python "C:\Users\liujianglong\.qoder\skills\ssh-unattended\scripts\ssh_command.py" "systemctl disable weread-selenium.service && systemctl stop weread-selenium.service && echo 'OK: systemd service disabled'" --csv "e:/Qoder_workspace/weread-challenge-selenium/docs/rk3566-oect-4-fnOS-deploy/password.csv"
```

### 步骤 2：写入新的 crontab

将以下内容写入远程主机的 `/tmp/weread-crontab` 文件，然后用 `crontab` 命令加载：

```cron
# === weread-multi: selenium lifecycle ===
# 02:25 启动 Selenium 容器（预热 5 分钟给浏览器初始化时间）
25 2 * * * cd /vol1/docker/mycontainers/weread-challenge-selenium-muti-user && docker compose up selenium -d
# 05:35 兜底清理：确保所有 app 停止，然后停止 Selenium
35 5 * * * cd /vol1/docker/mycontainers/weread-challenge-selenium-muti-user && docker compose stop app-1 app-2 2>/dev/null; docker compose stop selenium

# === weread-multi: liujl4735 (app-1) 02:30-04:00 ===
# 启动 app-1，后台 sleep 5400 秒（90 分钟）后自动停止
30 2 * * * cd /vol1/docker/mycontainers/weread-challenge-selenium-muti-user && docker compose up app-1 -d && (sleep 5400 && docker compose stop app-1) &

# === weread-multi: transition 04:01-04:02 ===
# 04:01 重启 Selenium，释放浏览器会话、清理残留（与 app-1 停止间隔 1 分钟）
1 4 * * * cd /vol1/docker/mycontainers/weread-challenge-selenium-muti-user && docker restart weread-challenge-selenium-muti-user
# 04:02 启动 app-2，后台 sleep 5280 秒（88 分钟）后自动停止（与 Selenium 重启间隔 1 分钟）
2 4 * * * cd /vol1/docker/mycontainers/weread-challenge-selenium-muti-user && docker compose up app-2 -d && (sleep 5280 && docker compose stop app-2) &

# === weread-multi: reboot recovery ===
# 服务器重启时检测时间窗口，在 02:25~05:35 内自动补启动
@reboot /bin/bash -c 'H=$(date +\%H); M=$(date +\%M); T=$((H*60+M)); if [ $T -ge 145 ] && [ $T -le 335 ]; then cd /vol1/docker/mycontainers/weread-challenge-selenium-muti-user && docker compose up selenium -d && sleep 30 && if [ $T -lt 240 ]; then docker compose up app-1 -d; elif [ $T -ge 242 ]; then docker compose up app-2 -d; fi; fi'

# === weread-multi: daily cleanup ===
# 每天 23:59 清理截图和日志文件
59 23 * * * cd /vol1/docker/mycontainers/weread-challenge-selenium-muti-user && find data -name screenshot-*.png -delete && find data -name output.log -delete

# system logrotate
*/30 * * * * /usr/sbin/logrotate /etc/logrotate.d/rsyslog > /dev/null 2>&1
```

通过 SSH 工具执行：

```powershell
python "C:\Users\liujianglong\.qoder\skills\ssh-unattended\scripts\ssh_command.py" "cat > /tmp/weread-crontab << 'CRONTAB_EOF'
# === weread-multi: selenium lifecycle ===
25 2 * * * cd /vol1/docker/mycontainers/weread-challenge-selenium-muti-user && docker compose up selenium -d
35 5 * * * cd /vol1/docker/mycontainers/weread-challenge-selenium-muti-user && docker compose stop app-1 app-2 2>/dev/null; docker compose stop selenium

# === weread-multi: liujl4735 (app-1) 02:30-04:00 ===
30 2 * * * cd /vol1/docker/mycontainers/weread-challenge-selenium-muti-user && docker compose up app-1 -d && (sleep 5400 && docker compose stop app-1) &

# === weread-multi: transition 04:01-04:02 ===
1 4 * * * cd /vol1/docker/mycontainers/weread-challenge-selenium-muti-user && docker restart weread-challenge-selenium-muti-user
2 4 * * * cd /vol1/docker/mycontainers/weread-challenge-selenium-muti-user && docker compose up app-2 -d && (sleep 5280 && docker compose stop app-2) &

# === weread-multi: reboot recovery ===
@reboot /bin/bash -c 'H=\$(date +\%H); M=\$(date +\%M); T=\$((H*60+M)); if [ $T -ge 145 ] && [ $T -le 335 ]; then cd /vol1/docker/mycontainers/weread-challenge-selenium-muti-user && docker compose up selenium -d && sleep 30 && if [ $T -lt 240 ]; then docker compose up app-1 -d; elif [ $T -ge 242 ]; then docker compose up app-2 -d; fi; fi'

# === weread-multi: daily cleanup ===
59 23 * * * cd /vol1/docker/mycontainers/weread-challenge-selenium-muti-user && find data -name screenshot-*.png -delete && find data -name output.log -delete

# system logrotate
*/30 * * * * /usr/sbin/logrotate /etc/logrotate.d/rsyslog > /dev/null 2>&1
CRONTAB_EOF
crontab /tmp/weread-crontab && echo 'OK: crontab installed' && crontab -l" --csv "e:/Qoder_workspace/weread-challenge-selenium/docs/rk3566-oect-4-fnOS-deploy/password.csv"
```

### 步骤 3：验证

执行以下命令确认 crontab 已正确加载：

```powershell
python "C:\Users\liujianglong\.qoder\skills\ssh-unattended\scripts\ssh_command.py" "crontab -l" --csv "e:/Qoder_workspace/weread-challenge-selenium/docs/rk3566-oect-4-fnOS-deploy/password.csv"
```

确认 systemd 服务已禁用：

```powershell
python "C:\Users\liujianglong\.qoder\skills\ssh-unattended\scripts\ssh_command.py" "systemctl is-enabled weread-selenium.service 2>&1; systemctl is-active weread-selenium.service 2>&1" --csv "e:/Qoder_workspace/weread-challenge-selenium/docs/rk3566-oect-4-fnOS-deploy/password.csv"
```

期望输出：
- `is-enabled` → `disabled`
- `is-active` → `inactive`

## 七、改造前后对比

| 项目 | 改造前 | 改造后 |
|---|---|---|
| 用户数 | 4 个（liujl4735、liujl3016、jpx155、jpx181） | 2 个（liujl4735、liujl3016） |
| 每日时间窗口 | 4 次/用户，每次 70 分钟 | 1 次，3 小时（02:30~05:30） |
| 运行模式 | app-1~4 错开调度，可能同时有 2 个 app 运行 | app-1 和 app-2 严格顺序运行，不重叠 |
| Selenium 运行时间 | 全天（开机自启） | 仅 02:25~05:35（约 3 小时） |
| 开机恢复 | systemd service | crontab @reboot + 时间窗口判断 |
| 交接动作 | 不涉及（各 app 独立周期） | 3 个动作间隔 1 分钟（04:00/04:01/04:02） |
| app 退出逻辑 | sleep 4200 → stop + restart selenium | app-1: sleep 5400 → stop；04:01 独立重启 selenium；app-2: sleep 5280 → stop |

## 八、注意事项

1. **crontab 中的 `%` 需要转义**：在 crontab 文件中，`%` 有特殊含义，`date` 命令中的 `%H`、`%M` 必须写为 `\%H`、`\%M`
2. **@reboot 中的 `$` 转义规则**：通过 SSH heredoc（`<< 'CRONTAB_EOF'`）写入时，需要区分两种情况：
   - **单引号外部的 `$`**（如 `\$((H*60+M))`）：需要 `\$` 转义，防止远程 shell 在处理 `cat` 命令时展开算术表达式
   - **单引号内部的 `$`**（如 `if [ $T -ge 145 ]`）：**不能**用 `\$`，因为单引号已保护变量不被展开，写入 `\$T` 会导致 crontab 执行时变量无法解析（BUG）
3. **sleep 后台进程**：`sleep` 命令末尾的 `&` 使其在后台运行，不会阻塞 crontab 执行；但如果 crontab 条目被多次触发（如手动重新安装 crontab），可能产生重复的后台进程
4. **05:35 兜底清理**：即使 app 的 sleep 因某种原因没有正常触发停止，05:35 的 crontab 也会强制停止所有容器，确保 Selenium 不会在非窗口时间运行
5. **fnOS 系统特殊性**：fnOS 会在某些情况下重置 systemd 单元文件，因此不使用 systemd 管理 Selenium，改用纯 crontab 方案更可靠
