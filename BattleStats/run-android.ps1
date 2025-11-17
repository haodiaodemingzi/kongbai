# 设置代理
$env:HTTP_PROXY="http://127.0.0.1:7897"
$env:HTTPS_PROXY="http://127.0.0.1:7897"

Write-Host "代理已设置: 127.0.0.1:7897" -ForegroundColor Green

# 运行 Android
npm run android
