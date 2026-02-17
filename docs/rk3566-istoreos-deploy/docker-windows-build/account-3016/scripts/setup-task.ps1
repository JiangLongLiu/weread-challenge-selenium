# account-3016 Windows 定时任务配置脚本
# 使用方式: 以管理员身份运行 PowerShell，然后执行 .\scripts\setup-task.ps1

$TaskNamePrefix = "WeRead-3016"
$WorkDir = "E:\dockers\weread-challenge-selenium-3016"

Write-Host "=========================================="
Write-Host "account-3016 定时任务配置 (Windows)"
Write-Host "=========================================="

# 检查工作目录是否存在
if (-not (Test-Path $WorkDir)) {
    Write-Host "错误: 工作目录不存在: $WorkDir"
    exit 1
}

# 删除已存在的定时任务
schtasks /Delete /TN "WeRead-3016" /F 2>$null
schtasks /Delete /TN "WeRead-3016-06" /F 2>$null
schtasks /Delete /TN "WeRead-3016-12" /F 2>$null
schtasks /Delete /TN "WeRead-3016-18" /F 2>$null

# 创建定时任务：0:00, 6:00, 12:00, 18:00
$times = @("00:00", "06:00", "12:00", "18:00")
foreach ($time in $times) {
    $taskName = "WeRead-3016-" + $time.Substring(0,2)
    $cmd = "powershell -NoProfile -Command cd $WorkDir; docker compose up -d"
    schtasks /Create /TN $taskName /TR $cmd /SC DAILY /ST $time /F
    Write-Host "创建: $taskName at $time"
}

Write-Host ""
Write-Host "完成! (每6小时执行一次: 0:00, 6:00, 12:00, 18:00)"
Write-Host ""

schtasks /Query /FO TABLE | findstr "WeRead"