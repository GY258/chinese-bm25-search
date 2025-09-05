# 🇨🇳 中文BM25文档检索服务

基于jieba分词和BM25算法的中文文档检索服务，专为中文文本优化。

## 🚀 快速开始

### 使用Docker部署 (推荐)

1. **克隆仓库**
```bash
git clone https://github.com/GY258/chinese-bm25-search.git
cd chinese-bm25-search
```

2. **准备文档**
```bash
# 将您的文档放入documents目录
mkdir -p documents
cp /path/to/your/documents/* documents/
```

3. **一键部署**
```bash
./deploy.sh
```

4. **访问服务**
- 服务地址: http://localhost
- API文档: http://localhost/
- 健康检查: http://localhost/health

### 手动部署

1. **安装依赖**
```bash
pip install -r requirements.txt
```

2. **构建索引**
```bash
python chinese_cli.py build-index
```

3. **启动服务**
```bash
python api_server.py
```

## 📡 API接口

### 搜索文档
```bash
curl -X POST http://localhost:5002/search \
  -H "Content-Type: application/json" \
  -d '{"query": "猪肝", "limit": 3}'
```

### 健康检查
```bash
curl http://localhost:5002/health
```

## 🔧 配置

- 文档目录: `documents/`
- 索引目录: `chinese_index/`
- 日志目录: `logs/`
- 端口: 5002

## 📊 性能

- 支持并发请求
- 平均响应时间 < 50ms
- 支持10,000+文档索引

## 🛠️ 开发

```bash
# 开发模式
python api_server.py

# 测试
python test_api.py

# 命令行搜索
python search.py "搜索词"
```

## 📝 许可证

MIT License
