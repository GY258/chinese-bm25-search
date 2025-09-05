#!/bin/bash

echo "🚀 部署中文BM25检索服务"
echo "========================"

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ Docker未安装，请先安装Docker"
    exit 1
fi

# 检查Docker Compose是否安装
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose未安装，请先安装Docker Compose"
    exit 1
fi

# 创建必要的目录
mkdir -p documents chinese_index logs ssl

# 停止现有服务
echo "🛑 停止现有服务..."
docker-compose down

# 构建新镜像
echo "🔨 构建Docker镜像..."
docker-compose build --no-cache

# 启动服务
echo "🚀 启动服务..."
docker-compose up -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 10

# 检查服务状态
echo "🔍 检查服务状态..."
if curl -f http://localhost:5002/health > /dev/null 2>&1; then
    echo "✅ 服务启动成功！"
    echo "🌐 访问地址: http://localhost"
    echo "📖 API文档: http://localhost/"
    echo "🔍 健康检查: http://localhost/health"
else
    echo "❌ 服务启动失败，请检查日志:"
    docker-compose logs chinese-search
fi
