# account-3016 删除定时任务脚本
# 使用方式: 以管理员身份运行 PowerShell，然后执行 .\scripts\remove-task.ps1

Write-Host "=========================================="
Write-Host "删除 account-3016 定时任务"
Write-Host "=========================================="

# 删除定时任务
schtasks /Delete /TN "WeRead-3016" /F 2>$null
schtasks /Delete /TN "WeRead-3016-06" /F 2>$null
schtasks /Delete /TN "WeRead-3016-12" /F 2>$null
schtasks /Delete /TN "WeRead-3016-18" /F 2>$null

Write-Host "已删除所有定时任务"
Write-Host ""

schtasks /Query /FO TABLE | findstr "WeRead" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "无残留定时任务"
}