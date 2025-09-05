# 🚀 中文BM25检索服务 - RESTful API 调用指南

## 📡 服务信息

- **服务地址**: `http://localhost:5002` (本地) 或 `http://YOUR_SERVER_IP:5002` (外部)
- **协议**: HTTP RESTful API
- **数据格式**: JSON
- **跨域支持**: ✅ 已启用 CORS
- **并发支持**: ✅ 多线程处理
- **响应编码**: UTF-8

## 🔧 **其他服务调用所需的信息**

### 1. **网络要求**
- 确保能访问服务器的 `5002` 端口
- 如果是外部调用，需要防火墙开放该端口

### 2. **HTTP客户端库** (任选其一)
```bash
# Python
pip install requests

# Node.js  
npm install axios

# Java
<dependency>
    <groupId>org.apache.httpcomponents</groupId>
    <artifactId>httpclient</artifactId>
</dependency>

# Go
go get -u github.com/go-resty/resty/v2
```

### 3. **基础配置**
- **Content-Type**: `application/json` (POST请求)
- **Accept**: `application/json`
- **字符编码**: UTF-8

## 📋 API 接口列表

### 1. **健康检查** `GET /health`
检查服务状态和搜索引擎是否就绪

**请求示例:**
```bash
curl -X GET "http://localhost:5002/health"
```

**响应示例:**
```json
{
  "status": "healthy",
  "service": "Chinese BM25 Retrieval Service", 
  "timestamp": "2024-12-28T12:20:30.123456",
  "search_engine_ready": true,
  "documents_count": 10,
  "vocabulary_size": 2111,
  "last_indexed": "2024-12-28T12:15:20.456789",
  "api_version": "1.0.0"
}
```

### 2. **搜索文档** `GET /search` 或 `POST /search`

#### GET 方式 (推荐用于简单查询)
```bash
curl -X GET "http://localhost:5002/search?query=猪肝&limit=3&snippets=true"
```

#### POST 方式 (推荐用于复杂查询)
```bash
curl -X POST "http://localhost:5002/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "猪肝制作方法",
    "limit": 5,
    "include_snippets": true
  }'
```

**参数说明:**
- `query` (必填): 搜索关键词
- `limit` (可选): 返回结果数量，默认10，最大50
- `include_snippets` (可选): 是否包含文档片段，默认true

**响应示例:**
```json
{
  "success": true,
  "query": "猪肝",
  "results_count": 1,
  "search_time_seconds": 0.0234,
  "results": [
    {
      "doc_id": 0,
      "score": 4.27,
      "path": "/Users/yuanan/Downloads/laicai_document/15秒火爆猪肝SOP20241228.txt",
      "title": "15秒火爆猪肝SOP20241228.txt",
      "length": 538,
      "chinese_chars": 1101,
      "relevance": "medium",
      "snippet": "15 秒爆猪肝 sop 产品标准..."
    }
  ],
  "timestamp": "2024-12-28T12:21:15.789012"
}
```

### 3. **系统统计** `GET /stats`
获取搜索引擎统计信息

```bash
curl -X GET "http://localhost:5002/stats"
```

**响应示例:**
```json
{
  "success": true,
  "statistics": {
    "documents_count": 10,
    "vocabulary_size": 2111,
    "average_document_length": 703.7,
    "total_chinese_characters": 22904,
    "bm25_parameters": {
      "k1": 1.5,
      "b": 0.6
    },
    "top_terms": [
      {"term": "制作", "frequency": 45},
      {"term": "标准", "frequency": 38}
    ],
    "last_indexed": "2024-12-28T12:15:20.456789"
  },
  "timestamp": "2024-12-28T12:22:00.123456"
}
```

### 4. **重建索引** `POST /build_index`
重新扫描并构建搜索索引

```bash
curl -X POST "http://localhost:5002/build_index"
```

### 5. **词汇信息** `GET /term/{词汇}`
获取特定词汇的详细信息

```bash
curl -X GET "http://localhost:5002/term/猪肝"
```

### 6. **API文档** `GET /`
获取完整API文档和服务状态

```bash
curl -X GET "http://localhost:5002/"
```

## 💻 **不同语言的调用示例**

### Python (requests)
```python
import requests
import json

# 基础配置
BASE_URL = "http://localhost:5002"
headers = {"Content-Type": "application/json"}

# 健康检查
def check_health():
    response = requests.get(f"{BASE_URL}/health")
    return response.json()

# 搜索文档
def search_documents(query, limit=10):
    data = {
        "query": query,
        "limit": limit,
        "include_snippets": True
    }
    response = requests.post(f"{BASE_URL}/search", 
                           headers=headers, 
                           json=data)
    return response.json()

# 使用示例
if __name__ == "__main__":
    # 检查服务状态
    health = check_health()
    print(f"服务状态: {health['status']}")
    
    # 搜索文档
    results = search_documents("猪肝制作", limit=3)
    print(f"找到 {results['results_count']} 个结果")
    for result in results['results']:
        print(f"- {result['title']} (评分: {result['score']:.2f})")
```

### Node.js (axios)
```javascript
const axios = require('axios');

const BASE_URL = 'http://localhost:5002';

// 健康检查
async function checkHealth() {
  try {
    const response = await axios.get(`${BASE_URL}/health`);
    return response.data;
  } catch (error) {
    console.error('健康检查失败:', error.message);
    return null;
  }
}

// 搜索文档
async function searchDocuments(query, limit = 10) {
  try {
    const response = await axios.post(`${BASE_URL}/search`, {
      query: query,
      limit: limit,
      include_snippets: true
    });
    return response.data;
  } catch (error) {
    console.error('搜索失败:', error.message);
    return null;
  }
}

// 使用示例
async function main() {
  // 检查服务
  const health = await checkHealth();
  console.log('服务状态:', health?.status);
  
  // 搜索文档
  const results = await searchDocuments('儿童套餐', 3);
  console.log(`找到 ${results?.results_count} 个结果`);
  results?.results.forEach(result => {
    console.log(`- ${result.title} (评分: ${result.score.toFixed(2)})`);
  });
}

main();
```

### Java (Spring RestTemplate)
```java
import org.springframework.web.client.RestTemplate;
import org.springframework.http.*;
import java.util.HashMap;
import java.util.Map;

public class ChineseSearchClient {
    private static final String BASE_URL = "http://localhost:5002";
    private final RestTemplate restTemplate = new RestTemplate();
    
    // 健康检查
    public Map<String, Object> checkHealth() {
        String url = BASE_URL + "/health";
        return restTemplate.getForObject(url, Map.class);
    }
    
    // 搜索文档
    public Map<String, Object> searchDocuments(String query, int limit) {
        String url = BASE_URL + "/search";
        
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        
        Map<String, Object> requestBody = new HashMap<>();
        requestBody.put("query", query);
        requestBody.put("limit", limit);
        requestBody.put("include_snippets", true);
        
        HttpEntity<Map<String, Object>> request = 
            new HttpEntity<>(requestBody, headers);
            
        return restTemplate.postForObject(url, request, Map.class);
    }
    
    // 使用示例
    public static void main(String[] args) {
        ChineseSearchClient client = new ChineseSearchClient();
        
        // 检查服务
        Map<String, Object> health = client.checkHealth();
        System.out.println("服务状态: " + health.get("status"));
        
        // 搜索文档
        Map<String, Object> results = client.searchDocuments("安全标准", 5);
        System.out.println("搜索结果: " + results.get("results_count"));
    }
}
```

### Go (resty)
```go
package main

import (
    "fmt"
    "github.com/go-resty/resty/v2"
)

const BaseURL = "http://localhost:5002"

type SearchRequest struct {
    Query           string `json:"query"`
    Limit          int    `json:"limit"`
    IncludeSnippets bool   `json:"include_snippets"`
}

type SearchResponse struct {
    Success      bool   `json:"success"`
    Query        string `json:"query"`
    ResultsCount int    `json:"results_count"`
    Results      []map[string]interface{} `json:"results"`
}

func main() {
    client := resty.New()
    
    // 健康检查
    var health map[string]interface{}
    _, err := client.R().
        SetResult(&health).
        Get(BaseURL + "/health")
    
    if err == nil {
        fmt.Printf("服务状态: %s\n", health["status"])
    }
    
    // 搜索文档
    request := SearchRequest{
        Query:           "汤圆制作",
        Limit:          3,
        IncludeSnippets: true,
    }
    
    var response SearchResponse
    _, err = client.R().
        SetHeader("Content-Type", "application/json").
        SetBody(request).
        SetResult(&response).
        Post(BaseURL + "/search")
        
    if err == nil {
        fmt.Printf("找到 %d 个结果\n", response.ResultsCount)
        for _, result := range response.Results {
            fmt.Printf("- %s (评分: %.2f)\n", 
                result["title"], result["score"])
        }
    }
}
```

## 🔒 **安全考虑**

### 生产环境部署建议:
1. **使用HTTPS**: 配置SSL证书
2. **API认证**: 添加Token或API Key验证
3. **请求限制**: 实现频率限制(Rate Limiting)
4. **日志监控**: 记录访问日志和错误日志

### 示例nginx反向代理配置:
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location /chinese-search/ {
        proxy_pass http://localhost:5002/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

## 📊 **性能特点**

- **响应时间**: 通常 < 50ms
- **并发支持**: 支持多线程并发请求
- **内存使用**: 约 100MB (包含索引)
- **搜索精度**: BM25算法，中文优化

## ❗ **错误处理**

所有API都会返回标准的HTTP状态码:
- `200`: 成功
- `400`: 请求参数错误
- `404`: 接口不存在  
- `500`: 服务器内部错误
- `503`: 服务不可用(搜索引擎未就绪)

错误响应格式:
```json
{
  "error": "错误描述",
  "message": "详细错误信息", 
  "code": "ERROR_CODE"
}
```

---

**🎉 您的中文BM25检索服务API已完全就绪！**

现在任何其他服务都可以通过HTTP请求来调用您的中文文档搜索功能了。
