# 🇨🇳 中文BM25文档检索服务

基于jieba分词和BM25算法的中文文档检索服务，专为中文文本优化。支持RESTful API调用，适合集成到其他系统中。

## ✨ 功能特性

- 🎯 **精准搜索**: BM25算法优化中文搜索
- 🚀 **高性能**: 支持10,000+文档索引
- 🌐 **RESTful API**: 完整的HTTP接口
- 📝 **中文优化**: jieba分词 + POS过滤
- 🐳 **Docker支持**: 一键部署
- 🔍 **并发处理**: 多线程支持
- 📊 **实时统计**: 系统状态监控

## 📋 系统要求

- **Python**: 3.8+
- **Docker**: 20.0+ (推荐)
- **内存**: 512MB+ (包含索引)
- **存储**: 100MB+ (文档和索引)

## 🚀 快速开始

### 方法1: Docker部署 (推荐)

#### 本地测试
```bash
# 1. 克隆项目
git clone https://github.com/GY258/chinese-bm25-search.git
cd chinese-bm25-search

# 2. 准备文档 (可选)
mkdir -p documents
cp /path/to/your/documents/* documents/

# 3. 一键部署
./deploy.sh

# 4. 验证服务
curl "http://127.0.0.1:5003/health"
curl "http://127.0.0.1:5003/search?query=猪肝&limit=2"
```

#### 远程服务器部署

##### 步骤1: 服务器准备
```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装Docker和Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 验证安装
docker --version
docker-compose --version
```

##### 步骤2: 上传项目
```bash
# 方法1: Git克隆
git clone https://github.com/GY258/chinese-bm25-search.git
cd chinese-bm25-search

# 方法2: SCP上传
# scp -r chinese-bm25-search user@server:/path/to/
```

##### 步骤3: 准备文档
```bash
# 创建文档目录
mkdir -p documents

# 上传您的文档
# scp your_documents/* user@server:/path/to/chinese-bm25-search/documents/
```

##### 步骤4: 配置防火墙
```bash
# 开放端口 (根据需要选择)
sudo ufw allow 5003/tcp  # API端口
sudo ufw allow 8080/tcp  # Nginx端口(可选)
sudo ufw --force enable
```

##### 步骤5: 部署服务
```bash
# 启动服务
./deploy.sh

# 或手动启动
docker-compose up --build -d

# 查看状态
docker-compose ps
docker-compose logs -f
```

##### 步骤6: 验证部署
```bash
# 测试健康检查
curl "http://your-server-ip:5003/health"

# 测试搜索功能
curl "http://your-server-ip:5003/search?query=猪肝&limit=2"

# 如果配置了nginx
curl "http://your-server-ip:8080/search?query=猪肝&limit=2"
```

### 方法2: 手动Python部署

#### 本地安装
```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 构建索引
python chinese_cli.py build-index

# 3. 启动服务
python api_server.py
```

#### 远程服务器Python部署
```bash
# 1. 安装Python环境
sudo apt install python3 python3-pip -y

# 2. 上传项目文件
scp -r chinese-bm25-search user@server:/home/user/

# 3. 在服务器上安装
cd /home/user/chinese-bm25-search
pip3 install -r requirements.txt

# 4. 构建索引
python3 chinese_cli.py build-index

# 5. 启动服务 (后台运行)
nohup python3 api_server.py > logs/api.log 2>&1 &

# 6. 查看状态
ps aux | grep api_server
tail -f logs/api.log
```

## 🔧 配置说明

### 环境变量
```bash
# API配置
API_HOST=0.0.0.0          # 监听地址
API_PORT=5002             # 监听端口
DEBUG=False               # 调试模式

# 路径配置
DOCUMENTS_DIR=/app/documents    # 文档目录
INDEX_DIR=/app/chinese_index    # 索引目录

# 搜索配置
DEFAULT_RESULTS_LIMIT=10  # 默认结果数量
MAX_RESULTS_LIMIT=50      # 最大结果数量
```

### Docker配置
```yaml
# docker-compose.yml
services:
  chinese-search:
    ports:
      - "5003:5002"  # 宿主机端口:容器端口
    environment:
      - API_PORT=5002
      - DEBUG=False
    volumes:
      - ./documents:/app/documents:ro
      - ./chinese_index:/app/chinese_index
```

## 📡 API使用文档

### 基础信息
- **基础URL**: `http://your-server:5003`
- **认证**: 无需认证
- **数据格式**: JSON
- **编码**: UTF-8

### 接口列表

#### 1. 健康检查
```bash
curl "http://your-server:5003/health"
```

#### 2. 搜索文档
```bash
# GET方式
curl "http://your-server:5003/search?query=猪肝&limit=3"

# POST方式 (推荐)
curl -X POST "http://your-server:5003/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "猪肝制作方法",
    "limit": 5,
    "include_snippets": true
  }'
```

#### 3. 系统统计
```bash
curl "http://your-server:5003/stats"
```

#### 4. 重建索引
```bash
curl -X POST "http://your-server:5003/build_index"
```

#### 5. API文档
```bash
curl "http://your-server:5003/"
```

### 响应示例
```json
{
  "success": true,
  "query": "猪肝",
  "results_count": 1,
  "search_time_seconds": 0.023,
  "results": [
    {
      "doc_id": 0,
      "score": 4.27,
      "title": "15秒火爆猪肝SOP20250816.md",
      "path": "/app/documents/15秒火爆猪肝SOP20250816.md",
      "length": 820,
      "chinese_chars": 1297,
      "relevance": "high",
      "snippet": "# 15秒火爆猪肝SOP..."
    }
  ]
}
```

## 🛠️ 故障排除

### 服务无法启动
```bash
# 检查端口占用
netstat -tlnp | grep 5003

# 查看详细日志
docker-compose logs chinese-search

# 检查Docker状态
docker ps -a
```

### 搜索无结果
```bash
# 1. 检查索引是否存在
ls -la chinese_index/

# 2. 重建索引
curl -X POST "http://your-server:5003/build_index"

# 3. 检查文档格式
file documents/*
```

### 连接超时
```bash
# 1. 检查防火墙
sudo ufw status

# 2. 检查Docker网络
docker network ls
docker inspect chinese-bm25-search-1_default

# 3. 测试本地连接
curl "http://127.0.0.1:5002/health"
```

### 内存不足
```bash
# 检查系统资源
free -h
df -h

# 清理Docker
docker system prune -a --volumes
```

## 🔒 生产环境配置

### 安全加固
```bash
# 1. 使用反向代理
sudo apt install nginx -y

# 2. 配置SSL (可选)
sudo certbot --nginx -d your-domain.com

# 3. 设置防火墙
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
```

### 性能优化
```bash
# 1. 调整Docker资源限制
docker-compose.yml 添加:
services:
  chinese-search:
    deploy:
      resources:
        limits:
          memory: 1G
        reservations:
          memory: 512M

# 2. 使用外部数据库存储 (高级)
# 可以将索引存储到Redis或PostgreSQL
```

### 监控配置
```bash
# 1. 健康检查脚本
#!/bin/bash
if curl -fs "http://localhost:5003/health" > /dev/null; then
    echo "✅ 服务正常"
    exit 0
else
    echo "❌ 服务异常"
    exit 1
fi

# 2. 设置定时任务
crontab -e
# 添加: */5 * * * * /path/to/health_check.sh
```

## 📊 性能指标

- **响应时间**: < 50ms (典型搜索)
- **并发处理**: 支持多线程
- **内存占用**: ~100MB (包含索引)
- **索引大小**: ~10MB (1000个文档)
- **搜索精度**: BM25算法优化

## 🧪 测试工具

### API测试
```bash
# 使用内置测试脚本
python test_api.py
```

### 搜索测试
```bash
# 命令行搜索
python search.py "搜索词"

# 服务测试
python test_service.py
```

## 📝 更新日志

### v1.0.0 (最新)
- ✅ 修复Flask初始化问题
- ✅ 添加中文POS过滤优化
- ✅ 改进搜索结果处理
- ✅ 完善Docker部署配置
- ✅ 添加完整的API文档

## 🤝 贡献指南

1. Fork项目
2. 创建特性分支: `git checkout -b feature/amazing-feature`
3. 提交更改: `git commit -m 'Add amazing feature'`
4. 推送分支: `git push origin feature/amazing-feature`
5. 创建Pull Request

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 📞 支持

- 📧 邮箱: your-email@example.com
- 🐛 问题反馈: [GitHub Issues](https://github.com/GY258/chinese-bm25-search/issues)
- 📖 文档: [API_GUIDE.md](API_GUIDE.md)

---

**🎉 您的中文BM25检索服务已准备就绪！**

现在您可以在本地和远程服务器上轻松部署和使用这个强大的中文文档搜索服务了。