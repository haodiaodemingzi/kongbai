#!/bin/bash

# React Native 项目自动化安装脚本

echo "=========================================="
echo "Battle Stats - React Native 项目安装"
echo "=========================================="
echo ""

# 检查 Node.js
echo "✓ 检查 Node.js..."
if ! command -v node &> /dev/null; then
    echo "✗ Node.js 未安装，请先安装 Node.js v14+"
    exit 1
fi
echo "✓ Node.js 版本: $(node --version)"
echo ""

# 检查 npm
echo "✓ 检查 npm..."
if ! command -v npm &> /dev/null; then
    echo "✗ npm 未安装"
    exit 1
fi
echo "✓ npm 版本: $(npm --version)"
echo ""

# 检查 Java
echo "✓ 检查 Java..."
if ! command -v java &> /dev/null; then
    echo "✗ Java 未安装，请先安装 JDK 11+"
    exit 1
fi
echo "✓ Java 版本: $(java -version 2>&1 | head -n 1)"
echo ""

# 清除旧的 node_modules
if [ -d "node_modules" ]; then
    echo "⚠ 检测到旧的 node_modules，正在清除..."
    rm -rf node_modules
    echo "✓ 清除完成"
fi

# 安装依赖
echo "📦 正在安装依赖..."
npm install --legacy-peer-deps

if [ $? -eq 0 ]; then
    echo "✓ 依赖安装成功"
else
    echo "✗ 依赖安装失败"
    exit 1
fi
echo ""

# 创建 .env 文件
if [ ! -f ".env" ]; then
    echo "📝 创建 .env 文件..."
    cp .env.example .env
    echo "✓ .env 文件已创建，请编辑配置 API URL"
fi
echo ""

# 完成
echo "=========================================="
echo "✓ 安装完成！"
echo "=========================================="
echo ""
echo "下一步："
echo "1. 编辑 .env 文件配置 API URL"
echo "2. 编辑 src/services/api.js 配置 API 基础 URL"
echo "3. 启动 Metro 服务器: npm start"
echo "4. 在另一个终端运行: npm run android"
echo ""
echo "更多信息请查看 QUICK_START.md"
