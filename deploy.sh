#!/usr/bin/env bash
set -euo pipefail

echo "🚀 部署中文BM25检索服务"
echo "========================"

# 选择 compose 命令
if command -v docker-compose >/dev/null 2>&1; then
  DC="docker-compose"
elif docker compose version >/dev/null 2>&1; then
  DC="docker compose"
else
  echo "❌ 未找到 docker compose，请安装"
  exit 1
fi

mkdir -p documents chinese_index logs ssl

echo "🛑 停止现有服务..."
$DC down || true

echo "�� 构建Docker镜像..."
$DC build 

echo "🚀 启动服务..."
$DC up -d

echo "⏳ 等待服务启动(最长 ~60s)..."

# 修复健康检查URL逻辑
HAS_5002_PUBLISHED=$($DC ps | grep -E '0\.0\.0\.0:5002|:::5002' || true)
if [[ -n "$HAS_5002_PUBLISHED" ]]; then
  HEALTH_URL="http://127.0.0.1:5002/health"
  ACCESS_URL="http://127.0.0.1:5002"
  API_PORT="5002"
else
  # 检查nginx是否映射到8080端口
  HAS_8080_PUBLISHED=$($DC ps | grep -E '0\.0\.0\.0:8080|:::8080' || true)
  if [[ -n "$HAS_8080_PUBLISHED" ]]; then
    HEALTH_URL="http://127.0.0.1:8080/health"
    ACCESS_URL="http://127.0.0.1:8080"
    API_PORT="5003"
  else
    HEALTH_URL="http://127.0.0.1/health"
    ACCESS_URL="http://127.0.0.1"
    API_PORT="5003"
  fi
fi

ok=0
for i in {1..30}; do
  if curl -fsS "$HEALTH_URL" >/dev/null 2>&1; then
    ok=1; break
  fi
  sleep 2
done

if [[ $ok -eq 1 ]]; then
  echo "✅ 服务启动成功！"
  
  # 检查索引是否存在
  echo "🔍 检查索引状态..."
  INDEX_STATUS=$(curl -s "http://127.0.0.1:$API_PORT/health" | grep -o '"documents_count":[0-9]*' | cut -d':' -f2 || echo "0")
  
  if [[ "$INDEX_STATUS" == "0" ]] || [[ -z "$INDEX_STATUS" ]]; then
    echo "📚 索引不存在或为空，开始构建索引..."
    
    # 等待服务完全就绪
    sleep 5
    
    # 构建索引
    echo "🔄 正在构建索引..."
    BUILD_RESPONSE=$(curl -s -X POST "http://127.0.0.1:$API_PORT/build_index" || echo "")
    
    if [[ -n "$BUILD_RESPONSE" ]]; then
      # 检查构建结果
      if echo "$BUILD_RESPONSE" | grep -q '"success":true'; then
        echo "✅ 索引构建成功！"
        
        # 获取最终统计信息
        FINAL_STATS=$(curl -s "http://127.0.0.1:$API_PORT/stats" || echo "")
        if [[ -n "$FINAL_STATS" ]]; then
          DOC_COUNT=$(echo "$FINAL_STATS" | grep -o '"documents_count":[0-9]*' | cut -d':' -f2 || echo "未知")
          VOCAB_SIZE=$(echo "$FINAL_STATS" | grep -o '"vocabulary_size":[0-9]*' | cut -d':' -f2 || echo "未知")
          echo "📊 索引统计: $DOC_COUNT 个文档, $VOCAB_SIZE 个词汇"
        fi
      else
        echo "⚠️  索引构建可能有问题，但服务已启动"
        echo "   响应: $BUILD_RESPONSE"
      fi
    else
      echo "⚠️  无法连接到索引构建API，但服务已启动"
    fi
  else
    echo "✅ 索引已存在 ($INDEX_STATUS 个文档)"
  fi
  
  echo ""
  echo "🌐 访问地址: $ACCESS_URL"
  echo "🏥 健康检查: $HEALTH_URL"
  echo "📖 API文档: $ACCESS_URL/docs"
  echo ""
  echo "🔍 测试搜索示例:"
  echo "   curl '$ACCESS_URL/search?query=藕汤&limit=3'"
  echo ""
  exit 0
fi

echo "❌ 服务未就绪，开始抓日志（自动识别容器）..."

# 自动找出 API 容器（匹配 5002 暴露或镜像名含 chinese-search）
API_CID=$(docker ps -q \
  --filter "publish=5002" \
  | head -n1)

if [[ -z "$API_CID" ]]; then
  API_CID=$(docker ps -q --filter "ancestor=chinese-bm25-search-1-chinese-search" | head -n1)
fi

# 自动找出 Nginx 容器（匹配 80 暴露且镜像含 nginx）
NGINX_CID=$(docker ps -q \
  --filter "ancestor=nginx" \
  --filter "publish=80" | head -n1)

echo "--- API logs ---"
if [[ -n "$API_CID" ]]; then
  docker logs --tail=200 "$API_CID" || true
else
  echo "(未找到 API 容器)"
fi

echo "--- Nginx logs ---"
if [[ -n "$NGINX_CID" ]]; then
  docker logs --tail=200 "$NGINX_CID" || true
else
  echo "(未找到 Nginx 容器)"
fi

exit 1