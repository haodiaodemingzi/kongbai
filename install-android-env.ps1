# Android 开发环境自动化安装脚本
# 以管理员身份运行此脚本

Write-Host "========================================" -ForegroundColor Green
Write-Host "Android 开发环境自动化安装脚本" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# 检查管理员权限
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
if (-not $isAdmin) {
    Write-Host "错误: 请以管理员身份运行此脚本!" -ForegroundColor Red
    exit 1
}

# 第 1 步：检查 Java
Write-Host "第 1 步: 检查 Java..." -ForegroundColor Yellow
try {
    $javaVersion = java -version 2>&1
    Write-Host "✓ Java 已安装: $javaVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Java 未安装，请先安装 JDK 11" -ForegroundColor Red
    Write-Host "下载地址: https://www.oracle.com/java/technologies/downloads/#java11" -ForegroundColor Cyan
    exit 1
}

# 第 2 步：设置 JAVA_HOME
Write-Host ""
Write-Host "第 2 步: 设置 JAVA_HOME..." -ForegroundColor Yellow
$javaPath = "C:\Program Files\Java\jdk-11"
if (Test-Path $javaPath) {
    [Environment]::SetEnvironmentVariable("JAVA_HOME", $javaPath, "User")
    Write-Host "✓ JAVA_HOME 已设置为: $javaPath" -ForegroundColor Green
} else {
    Write-Host "✗ 未找到 JDK 11，请检查安装路径" -ForegroundColor Red
    exit 1
}

# 第 3 步：检查 Android SDK
Write-Host ""
Write-Host "第 3 步: 检查 Android SDK..." -ForegroundColor Yellow
$androidHome = "$env:USERPROFILE\AppData\Local\Android\Sdk"
if (Test-Path $androidHome) {
    [Environment]::SetEnvironmentVariable("ANDROID_HOME", $androidHome, "User")
    Write-Host "✓ ANDROID_HOME 已设置为: $androidHome" -ForegroundColor Green
} else {
    Write-Host "⚠ Android SDK 未找到，请先安装 Android Studio" -ForegroundColor Yellow
    Write-Host "下载地址: https://developer.android.com/studio" -ForegroundColor Cyan
}

# 第 4 步：更新 PATH
Write-Host ""
Write-Host "第 4 步: 更新 PATH..." -ForegroundColor Yellow
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
$pathsToAdd = @(
    "$env:JAVA_HOME\bin",
    "$androidHome\platform-tools",
    "$androidHome\tools"
)

foreach ($path in $pathsToAdd) {
    if ($userPath -notlike "*$path*") {
        $userPath += ";$path"
        Write-Host "✓ 已添加: $path" -ForegroundColor Green
    }
}

[Environment]::SetEnvironmentVariable("Path", $userPath, "User")

# 第 5 步：验证环境
Write-Host ""
Write-Host "第 5 步: 验证环境..." -ForegroundColor Yellow
Write-Host ""

# 刷新环境变量
$env:JAVA_HOME = [Environment]::GetEnvironmentVariable("JAVA_HOME", "User")
$env:ANDROID_HOME = [Environment]::GetEnvironmentVariable("ANDROID_HOME", "User")
$env:Path = [Environment]::GetEnvironmentVariable("Path", "User")

try {
    $javaCheck = java -version 2>&1
    Write-Host "✓ Java 版本: $javaCheck" -ForegroundColor Green
} catch {
    Write-Host "✗ Java 检查失败" -ForegroundColor Red
}

if (Test-Path "$env:ANDROID_HOME\platform-tools\adb.exe") {
    $adbVersion = & "$env:ANDROID_HOME\platform-tools\adb.exe" version
    Write-Host "✓ ADB 版本: $adbVersion" -ForegroundColor Green
} else {
    Write-Host "⚠ ADB 未找到，请确保 Android SDK 已安装" -ForegroundColor Yellow
}

# 完成
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "✓ 环境配置完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "下一步:" -ForegroundColor Cyan
Write-Host "1. 关闭并重新打开 PowerShell"
Write-Host "2. 运行: cd c:\coding\kongbai\mobile"
Write-Host "3. 运行: npm install --legacy-peer-deps"
Write-Host "4. 运行: npm start"
Write-Host "5. 在另一个终端运行: npm run android"
Write-Host ""
