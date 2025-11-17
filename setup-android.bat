@echo off
REM Android 开发环境设置脚本

echo.
echo ========================================
echo Android 开发环境设置
echo ========================================
echo.

REM 检查管理员权限
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo 错误: 请以管理员身份运行此脚本!
    pause
    exit /b 1
)

REM 运行 PowerShell 脚本
powershell -ExecutionPolicy Bypass -File "%~dp0install-android-env.ps1"

pause
