# 贵港旅游智能助手 - 一键启动脚本 (PowerShell)
# 启动 Flask + cpolar，自动显示公网地址

$ErrorActionPreference = "Stop"
$FlaskPort = 5001
$CpolarPath = "cpolar"  # 假设 cpolar 已在 PATH 中，否则改为完整路径

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "  贵港旅游智能助手 v4.0 - 一键启动" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# 检查 cpolar 是否可用
try {
    $null = & $CpolarPath version 2>&1
    Write-Host "[✓] cpolar 已安装" -ForegroundColor Green
} catch {
    Write-Host "[✗] 未找到 cpolar，请先安装: https://www.cpolar.com/download" -ForegroundColor Red
    Write-Host "   或设置脚本中的 `$CpolarPath 为 cpolar.exe 的完整路径" -ForegroundColor Yellow
    pause
    exit 1
}

# 设置 LLM API 环境变量（OpenClaw/Hermes 本地 API）
$env:LLM_API_BASE = "http://127.0.0.1:52863/v1"
$env:LLM_API_KEY = "6732b74443c351d8f61931de098587f01ff5c552af051cd9"
$env:LLM_MODEL = "openclaw/main"  # 使用主 Agent 的模型

Write-Host "[1/4] 启动 Flask 服务..." -ForegroundColor Yellow
$FlaskProcess = Start-Process -FilePath "python" -ArgumentList "app.py" `
    -WorkingDirectory $PSScriptRoot `
    -PassThru `
    -WindowStyle Normal

Start-Sleep -Seconds 3

# 检查 Flask 是否启动成功
try {
    $Response = Invoke-WebRequest -Uri "http://127.0.0.1:$FlaskPort" -UseBasicParsing -TimeoutSec 5
    Write-Host "[✓] Flask 服务启动成功 (PID: $($FlaskProcess.Id))" -ForegroundColor Green
} catch {
    Write-Host "[✗] Flask 服务启动失败，请检查 app.py" -ForegroundColor Red
    Stop-Process -Id $FlaskProcess.Id -Force -ErrorAction SilentlyContinue
    pause
    exit 1
}

Write-Host "[2/4] 启动 cpolar 隧道..." -ForegroundColor Yellow
$CpolarLogFile = Join-Path $PSScriptRoot "cpolar.log"
$CpolarProcess = Start-Process -FilePath $CpolarPath -ArgumentList "http", $FlaskPort `
    -PassThru `
    -RedirectStandardOutput $CpolarLogFile `
    -WindowStyle Hidden

Start-Sleep -Seconds 5

Write-Host "[3/4] 获取公网地址..." -ForegroundColor Yellow
# 从 cpolar 日志中提取公网地址
$PubUrl = $null
$CpolarInfoUrl = "http://127.0.0.1:4040/api/tunnels"  # cpolar 本地管理 API

try {
    $Tunnels = Invoke-RestMethod -Uri $CpolarInfoUrl -TimeoutSec 3
    $PubUrl = $Tunnels.tunnels[0].public_url
} catch {
    # 如果本地 API 不可用，尝试从日志文件读取（cpolar 免费版输出格式）
    if (Test-Path $CpolarLogFile) {
        $LogContent = Get-Content $CpolarLogFile -Tail 20
        foreach ($Line in $LogContent) {
            if ($Line -match "https?://[a-z0-9\-]+\.cpolar\.top") {
                $PubUrl = $Matches[0]
                break
            }
        }
    }
}

Write-Host ""
Write-Host "==================================================" -ForegroundColor Green
Write-Host "  服务启动完成！" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Green
Write-Host "  本地地址: <address></address>" -ForegroundColor Cyan
if ($PubUrl) {
    Write-Host "  公网地址: $PubUrl" -ForegroundColor Cyan
    Write-Host "            $($PubUrl -replace '^https?', 'https')" -ForegroundColor Cyan
} else {
    Write-Host "  公网地址: 获取失败，请访问 http://127.0.0.1:4040 查看" -ForegroundColor Yellow
}
Write-Host "==================================================" -ForegroundColor Green
Write-Host ""
Write-Host "[提示] 按 Ctrl+C 停止服务" -ForegroundColor Yellow
Write-Host "[提示] Flask PID: $($FlaskProcess.Id)  |  cpolar PID: $($CpolarProcess.Id)" -ForegroundColor Gray
Write-Host ""

# 保持脚本运行，等待用户中断
try {
    Write-Host "服务运行中... (按 Ctrl+C 停止)" -ForegroundColor Gray
    while ($true) {
        Start-Sleep -Seconds 5
        # 检查进程是否还在运行
        if ($FlaskProcess.HasExited) {
            Write-Host "[!] Flask 进程已退出" -ForegroundColor Red
            break
        }
        if ($CpolarProcess.HasExited) {
            Write-Host "[!] cpolar 进程已退出" -ForegroundColor Red
            break
        }
    }
} finally {
    Write-Host "正在停止服务..." -ForegroundColor Yellow
    Stop-Process -Id $FlaskProcess.Id -Force -ErrorAction SilentlyContinue
    Stop-Process -Id $CpolarProcess.Id -Force -ErrorAction SilentlyContinue
    Write-Host "[✓] 服务已停止" -ForegroundColor Green
}
