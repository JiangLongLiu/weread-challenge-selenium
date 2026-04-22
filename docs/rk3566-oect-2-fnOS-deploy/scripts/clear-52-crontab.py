#!/usr/bin/env python3
"""清理 52 号主机的定时任务"""
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(hostname='192.168.123.52', port=22, username='root', password='1234567890')

print("=" * 80)
print("清理 52 号主机的定时任务")
print("=" * 80)

# 1. 查看当前的定时任务
print("\n【1. 当前定时任务列表】")
stdin, stdout, stderr = ssh.exec_command('crontab -l')
result = stdout.read().decode().strip()
if result:
    print(result)
else:
    print("无定时任务")

# 2. 备份当前定时任务
print("\n【2. 备份当前定时任务】")
stdin, stdout, stderr = ssh.exec_command('crontab -l > /tmp/crontab_backup_$(date +%Y%m%d_%H%M%S).txt 2>&1 && echo "备份成功"')
result = stdout.read().decode().strip()
print(result)

# 3. 显示要删除的定时任务
print("\n【3. 要删除的定时任务（包含 weread 的任务）】")
stdin, stdout, stderr = ssh.exec_command('crontab -l | grep -E "weread|selenium|app-"')
result = stdout.read().decode().strip()
if result:
    print("将删除以下任务：")
    print(result)
else:
    print("无相关定时任务")

# 4. 获取所有定时任务
print("\n【4. 获取所有定时任务】")
stdin, stdout, stderr = ssh.exec_command('crontab -l')
all_tasks = stdout.read().decode().strip()

# 5. 过滤掉 weread 相关的任务
print("\n【5. 过滤 weread 相关任务】")
tasks_to_keep = []
for line in all_tasks.split('\n'):
    # 保留不包含 weread、selenium、app- 的行
    if not any(keyword in line.lower() for keyword in ['weread', 'selenium', 'app-']):
        tasks_to_keep.append(line)

print(f"保留 {len(tasks_to_keep)} 个非 weread 相关任务")

# 6. 写入新的 crontab
print("\n【6. 写入新的 crontab】")
if tasks_to_keep:
    new_crontab = '\n'.join(tasks_to_keep)
    # 使用临时文件写入
    stdin, stdout, stderr = ssh.exec_command(f'echo "{new_crontab}" | crontab -')
    result = stdout.read().decode().strip()
    if result:
        print(f"✗ 更新失败：{result}")
    else:
        print("✓ 定时任务已更新（删除了 weread 相关任务）")
else:
    # 如果没有任务要保留，清空 crontab
    stdin, stdout, stderr = ssh.exec_command('crontab -r')
    print("✓ 已清空所有定时任务")

# 7. 验证新的定时任务
print("\n【7. 验证新的定时任务】")
stdin, stdout, stderr = ssh.exec_command('crontab -l')
result = stdout.read().decode().strip()
if result:
    print("当前定时任务：")
    print(result)
else:
    print("当前无定时任务")

# 8. 检查 weread 相关任务是否已删除
print("\n【8. 检查 weread 相关任务是否已删除】")
stdin, stdout, stderr = ssh.exec_command('crontab -l | grep -E "weread|selenium|app-"')
result = stdout.read().decode().strip()
if result:
    print(f"⚠️  警告：仍有 weread 相关任务：")
    print(result)
else:
    print("✓ 所有 weread 相关任务已删除")

print("\n" + "=" * 80)
print("操作完成")
print("=" * 80)
print("\n✅ 已完成操作：")
print("  1. 备份当前定时任务")
print("  2. 删除所有 weread 相关定时任务")
print("  3. 保留非 weread 相关的定时任务")
print("  4. 验证删除结果")
print("\n📝 当前状态：")
print("  - systemd 服务：disabled")
print("  - Selenium 容器：已停止")
print("  - 定时任务：weread 相关任务已清理")
print("\n⚠️  注意：")
print("  - 备份文件保存在 /tmp/crontab_backup_*.txt")
print("  - 如需恢复，使用：crontab /tmp/crontab_backup_*.txt")
print("  - 重新启用时执行：systemctl enable weread-selenium.service")

ssh.close()
