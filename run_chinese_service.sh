#!/bin/bash

echo "🇨🇳 中文BM25检索服务启动脚本"
echo "============================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ 需要Python 3"
    exit 1
fi

# Navigate to service directory
cd "$(dirname "$0")"

# Check if dependencies are installed
if ! python -c "import jieba" 2>/dev/null; then
    echo "📦 安装依赖..."
    python -m pip install -r requirements.txt
fi

# Check if index exists
if [ ! -f "chinese_index/chinese_documents.json" ]; then
    echo "📊 构建中文索引..."
    python chinese_cli.py build-index
fi

echo "🚀 启动中文BM25检索服务..."
echo "服务地址: http://localhost:5001"
echo "API文档: http://localhost:5001/"
echo "按 Ctrl+C 停止服务"
echo ""

python chinese_api.py
