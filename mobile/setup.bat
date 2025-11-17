@echo off
REM React Native 项目自动化安装脚本 (Windows)

echo.
echo ==========================================
echo Battle Stats - React Native 项目安装
echo ==========================================
echo.

REM 检查 Node.js
echo 检查 Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo 错误: Node.js 未安装，请先安装 Node.js v14+
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('node --version') do set NODE_VERSION=%%i
echo 正常: Node.js 版本 %NODE_VERSION%
echo.

REM 检查 npm
echo 检查 npm...
npm --version >nul 2>&1
if errorlevel 1 (
    echo 错误: npm 未安装
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('npm --version') do set NPM_VERSION=%%i
echo 正常: npm 版本 %NPM_VERSION%
echo.

REM 检查 Java
echo 检查 Java...
java -version >nul 2>&1
if errorlevel 1 (
    echo 错误: Java 未安装，请先安装 JDK 11+
    pause
    exit /b 1
)
echo 正常: Java 已安装
echo.

REM 清除旧的 node_modules
if exist "node_modules" (
    echo 警告: 检测到旧的 node_modules，正在清除...
    rmdir /s /q node_modules
    echo 正常: 清除完成
)

REM 安装依赖
echo.
echo 正在安装依赖...
call npm install --legacy-peer-deps

if errorlevel 1 (
    echo 错误: 依赖安装失败
    pause
    exit /b 1
)
echo 正常: 依赖安装成功
echo.

REM 创建 .env 文件
if not exist ".env" (
    echo 创建 .env 文件...
    copy .env.example .env
    echo 正常: .env 文件已创建，请编辑配置 API URL
)
echo.

REM 完成
echo ==========================================
echo 正常: 安装完成！
echo ==========================================
echo.
echo 下一步:
echo 1. 编辑 .env 文件配置 API URL
echo 2. 编辑 src/services/api.js 配置 API 基础 URL
echo 3. 启动 Metro 服务器: npm start
echo 4. 在另一个终端运行: npm run android
echo.
echo 更多信息请查看 QUICK_START.md
echo.
pause
