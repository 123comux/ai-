# ============================================================
# 线上验收（curl 版）
#
# 为什么不用 tools/check_live.py：python-urllib/requests 的 TLS 指纹会被
# Cloudflare Bot Fight 判定为机器人并返回 403 error code: 1010（浏览器与 curl 正常）。
# 因此线上验收改用 curl 执行 20 项检查。
#
# 用法：
#   pwsh tools/check-live-curl.ps1 -Base https://ai-h5.pages.dev
#   pwsh tools/check-live-curl.ps1 -Base https://ai-h5.pages.dev -Phone 13800000000
# ============================================================
param(
  [Parameter(Mandatory = $true)][string]$Base,
  [string]$Phone = ''
)

$ErrorActionPreference = 'Stop'
$UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'
$Base = $Base.TrimEnd('/')
$Tmp = Join-Path $env:TEMP ('livecheck-' + [guid]::NewGuid().ToString('N').Substring(0, 8))
New-Item -ItemType Directory -Force -Path $Tmp | Out-Null

$pass = 0; $fail = 0
function Ok($label, $cond, $detail = '') {
  if ($cond) { $script:pass++; Write-Host ("  [OK]   {0,-44} {1}" -f $label, $detail) }
  else { $script:fail++; Write-Host ("  [FAIL] {0,-44} {1}" -f $label, $detail) -ForegroundColor Red }
}

function Fetch($method, $path, $token = '', $bodyFile = '', $extra = @()) {
  $out = Join-Path $Tmp 'body.bin'
  $hdr = Join-Path $Tmp 'head.txt'
  $args = @('-s', '-w', '%{http_code}', '-D', $hdr, '-o', $out, '--compressed', '--max-time', '90', '-A', $UA,
    '-H', 'Accept: application/json', '-X', $method)
  if ($token) { $args += @('-H', "Authorization: Bearer $token") }
  if ($bodyFile) { $args += @('-H', 'Content-Type: application/json', '--data-binary', "@$bodyFile") }
  if ($extra.Count) { $args += $extra }
  $args += ($Base + $path)
  $code = & curl.exe @args
  $bytes = @()
  if (Test-Path $out) { $bytes = [IO.File]::ReadAllBytes($out) }
  $json = $null
  if ($bytes.Length -gt 0 -and ($bytes[0] -eq 123 -or $bytes[0] -eq 91)) {
    try { $json = [IO.File]::ReadAllText($out, [Text.Encoding]::UTF8) | ConvertFrom-Json } catch { $json = $null }
  }
  $headers = @{}
  if (Test-Path $hdr) {
    Get-Content $hdr | ForEach-Object {
      if ($_ -match '^([A-Za-z0-9-]+):\s*(.*)$') { $headers[$Matches[1].ToLower()] = $Matches[2].Trim() }
    }
  }
  return @{ code = [int]$code; size = $bytes.Length; json = $json; headers = $headers }
}

function Count($obj) {
  if ($null -eq $obj) { return -1 }
  if ($obj -is [array]) { return $obj.Count }
  return 1
}

Write-Host "`n=== 线上验收：$Base ===`n"

Write-Host '--- 1. 前端与静态资源 ---'
$r = Fetch 'GET' '/'
Ok '首页 200' ($r.code -eq 200) "HTTP $($r.code), $($r.size) B"
$html = ''
if (Test-Path (Join-Path $Tmp 'body.bin')) { $html = [IO.File]::ReadAllText((Join-Path $Tmp 'body.bin'), [Text.Encoding]::UTF8) }
Ok 'viewport 响应式（device-width）' ($html -match 'width=device-width')
$r = Fetch 'GET' '/static/covers/project-0.png'
Ok '静态封面图 200' ($r.code -eq 200) "HTTP $($r.code), $($r.size) B"

Write-Host '--- 2. 只读内容接口（匿名） ---'
$r = Fetch 'GET' '/api'
Ok '/api 探活' ($r.code -eq 200) "HTTP $($r.code)"
$r = Fetch 'GET' '/api/courses'
Ok '课程列表有数据' ($r.code -eq 200 -and (Count $r.json) -ge 10) "HTTP $($r.code), $(Count $r.json) 条"
$r = Fetch 'GET' '/api/videos'
Ok '视频列表有数据' ($r.code -eq 200 -and (Count $r.json) -ge 10) "HTTP $($r.code), $(Count $r.json) 条"
$r = Fetch 'GET' '/api/projects'
Ok '项目列表有数据' ($r.code -eq 200 -and (Count $r.json) -ge 1) "HTTP $($r.code), $(Count $r.json) 条"
$r = Fetch 'GET' '/api/learning-paths'
Ok '学习路径有数据' ($r.code -eq 200 -and (Count $r.json) -ge 1) "HTTP $($r.code), $(Count $r.json) 条"
$r = Fetch 'GET' '/api/content/banners'
Ok '轮播图有数据' ($r.code -eq 200 -and (Count $r.json) -ge 1) "HTTP $($r.code), $(Count $r.json) 条"
$r = Fetch 'GET' '/api/content/directions'
Ok '学习方向有数据' ($r.code -eq 200 -and (Count $r.json) -ge 1) "HTTP $($r.code), $(Count $r.json) 条"
$r = Fetch 'GET' '/api/courses/topics'
Ok '课程话题接口' ($r.code -eq 200) "HTTP $($r.code)"
$r = Fetch 'GET' '/api/assessment/questions?count=2'
Ok '测评题库可取' ($r.code -eq 200 -and (Count $r.json) -eq 2) "HTTP $($r.code), $(Count $r.json) 条"
$r = Fetch 'GET' '/api/ai/models'
Ok 'AI 模型列表' ($r.code -eq 200) "HTTP $($r.code)"

Write-Host '--- 3. 鉴权边界（未登录必须挡住） ---'
foreach ($p in @('/api/auth/me', '/api/deposit/status', '/api/admin/users', '/api/community/teams/mine')) {
  $r = Fetch 'GET' $p
  Ok "未登录访问 $p" ($r.code -eq 401) "HTTP $($r.code)"
}

Write-Host '--- 4. 登录链路 ---'
$loginFile = Join-Path $Tmp 'login.json'
$testPhone = if ($Phone) { $Phone } else { '13800000000' }
[IO.File]::WriteAllText($loginFile, '{"phone":"' + $testPhone + '"}', [Text.Encoding]::ASCII)
$r = Fetch 'POST' '/api/auth/h5-login' '' $loginFile
$token = ''
if ($r.json -and $r.json.token) { $token = $r.json.token }
Ok 'POST 手机号登录签发 token' ($r.code -eq 200 -and $token.Length -gt 10) "HTTP $($r.code)"
if ($token) {
  $r = Fetch 'GET' '/api/auth/me' $token
  Ok '带 token 访问 /api/auth/me' ($r.code -eq 200) "HTTP $($r.code)"
}

Write-Host '--- 5. 安全：开发后门必须关闭 ---'
$fakeFile = Join-Path $Tmp 'fake.json'
[IO.File]::WriteAllText($fakeFile, '{"code":"fake-code-for-security-check"}', [Text.Encoding]::ASCII)
$r = Fetch 'POST' '/api/auth/wechat-login' '' $fakeFile
Ok '假 code 登录必须失败（DEV_MODE=false）' ($r.code -ne 200) "HTTP $($r.code)"
$r = Fetch 'GET' '/api/auth/dev/config'
$imp = $false
if ($r.json -and $r.json.PSObject.Properties.Name -contains 'impersonate_enabled') { $imp = [bool]$r.json.impersonate_enabled }
Ok 'dev/config 显示模拟用户已关闭' ($r.code -eq 200 -and -not $imp) "impersonate_enabled=$imp"
$r = Fetch 'POST' '/api/auth/dev/impersonate?user_id=1' '' $fakeFile
Ok 'dev 模拟切换用户接口已拒绝' ($r.code -ne 200) "HTTP $($r.code)"

Write-Host '--- 6. 边缘缓存（匿名只读接口） ---'
$h1 = (Fetch 'GET' '/api/content/banners').headers
$h2 = (Fetch 'GET' '/api/content/banners').headers
Ok '边缘缓存生效（第二次 HIT）' ($h2['x-edge-cache'] -eq 'HIT') "第一次=$($h1['x-edge-cache']) 第二次=$($h2['x-edge-cache'])"
$r = Fetch 'GET' '/api/content/banners'
$rAuth = Fetch 'GET' '/api/content/banners' 'faketoken-for-cache-test'
Ok '带 token 请求不进缓存' ($rAuth.headers['x-edge-cache'] -ne 'HIT') "x-edge-cache=$($rAuth.headers['x-edge-cache'])"

Write-Host "`n=== 结果：通过 $pass 项，失败 $fail 项 ==="
Remove-Item -Recurse -Force $Tmp -ErrorAction SilentlyContinue
if ($fail -gt 0) { exit 1 }
