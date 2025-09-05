#!/bin/bash

echo "🚀 启动中文BM25检索API服务"
echo "=========================="

# 检查Python环境
if ! command -v python &> /dev/null; then
    echo "❌ Python未安装"
    exit 1
fi

# 进入服务目录
cd "$(dirname "$0")"

# 检查依赖
echo "📦 检查依赖..."
python -c "import flask, jieba, numpy" 2>/dev/null || {
    echo "⚠️  安装依赖中..."
    pip install -r requirements.txt flask-cors
}

# 检查索引
if [ ! -f "chinese_index/chinese_documents.json" ]; then
    echo "📊 构建索引..."
    python chinese_cli.py build-index
fi

# 杀掉已有进程
pkill -f api_server.py 2>/dev/null
pkill -f test_service.py 2>/dev/null

echo "🌐 启动API服务器..."
echo "📡 地址: http://localhost:5002"
echo "📖 文档: http://localhost:5002/"
echo "🛑 按 Ctrl+C 停止服务"
echo ""

# 启动服务
python api_server.py
