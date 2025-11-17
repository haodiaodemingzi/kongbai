# 设置代理
$env:HTTP_PROXY="http://127.0.0.1:7897"
$env:HTTPS_PROXY="http://127.0.0.1:7897"
$env:JAVA_HOME="C:\Program Files\Java\jdk-25"
$env:PATH="C:\Program Files\Java\jdk-25\bin;$env:PATH"

Write-Host "环境配置完成" -ForegroundColor Green
Write-Host "代理: 127.0.0.1:7897" -ForegroundColor Cyan
Write-Host "Java: JDK 25" -ForegroundColor Cyan

# 生成原生代码
Write-Host "`n生成原生 Android 项目..." -ForegroundColor Yellow
npx expo prebuild --platform android

# 运行
Write-Host "`n启动应用..." -ForegroundColor Yellow
npx expo run:android
