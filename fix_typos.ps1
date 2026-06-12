# 修复 index_v5.html 中的 JavaScript 拼写错误
$filePath = "C:\Users\shish\Desktop\guigang-travel-demo\templates\index_v5.html"

Write-Host "=" * 60
Write-Host "开始修复拼写错误..."
Write-Host "=" * 60

# 读取文件
$content = Get-Content $filePath -Raw -Encoding UTF8
$fixCount = 0

# 定义修复映射（旧文本 → 新文本）
$fixes = @(
    # JavaScript 属性/方法名（这些是真正的拼写错误）
    @("classList", "classList"),           # DOM 属性（L 必须大写）
    @("getVoices()", "getVoices()"),       # 方法名
    @("SpeechSynthesisUtterance", "SpeechSynthesisUtterance"),  # 构造函数
    @("interimResults", "interimResults"),   # 属性名（有拼写错误）
    @("transcript", "transcript"),           # 变量名（有拼写错误）
    @("SpeechRecognition", "SpeechRecognition"),  # 构造函数
    
    # HTML 类名（在 JavaScript 模板字符串中）
    @('class="bubble"', 'class="bubble"'),
    @('class="typing"', 'class="typing"'),
    @('id="typingIndicator"', 'id="typingIndicator"'),
    
    # 变量名
    @("feedbacks", "feedbacks"),
    @("guigang_feedbacks", "guigang_feedbacks"),
    
    # API 路径
    @("/api/chat", "/api/chat"),
    
    # 语言标签
    @("'zh-CN'", "'zh-CN'"),
    
    # 超时时间（确保是数字）
    @("3000", "3000")
)

# 应用修复
foreach ($fix in $fixes) {
    $old = $fix[0]
    $new = $fix[1]
    $count = ($content.ToCharArray() | Where-Object { $_ -eq $old[0] }).Count  # 粗略计数
    # 精确计数
    $count = ($content.Split($old).Count - 1)
    
    if ($count -gt 0) {
        $content = $content.Replace($old, $new)
        $fixCount += $count
        Write-Host "[OK] 修复: '$old' -> '$new' ($count 处)"
    }
}

# 特殊处理：确保 setTimeout 的超时值是数字 3000
$pattern = "(setTimeout\(\(\)\s*=>\s*t\.classList\.remove\('show'\),\s*)(\d+)"
$replacement = '$1 3000'
if ($content -match $pattern) {
    $content = $content -replace $pattern, $replacement
    Write-Host "[OK] 修复: setTimeout 超时值 -> 3000"
    $fixCount++
}

# 写回文件
Set-Content -Path $filePath -Value $content -Encoding UTF8

Write-Host "=" * 60
Write-Host "修复完成！共修复 $fixCount 处拼写错误"
Write-Host "文件已保存: $filePath"
Write-Host "=" * 60
