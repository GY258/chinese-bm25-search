#!/usr/bin/env python3
"""
API接口测试工具
"""

import requests
import json
import time

BASE_URL = "http://localhost:5002"

def test_health():
    """测试健康检查"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ 健康检查成功:")
            print(f"   状态: {data.get('status')}")
            print(f"   文档数: {data.get('documents_count')}")
            print(f"   词汇量: {data.get('vocabulary_size')}")
            return True
        else:
            print(f"❌ 健康检查失败: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return False

def test_search(query="猪肝", limit=2):
    """测试搜索接口"""
    try:
        data = {
            "query": query,
            "limit": limit,
            "include_snippets": True
        }
        response = requests.post(
            f"{BASE_URL}/search",
            headers={"Content-Type": "application/json"},
            json=data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 搜索 '{query}' 成功:")
            print(f"   找到: {result.get('results_count')} 个结果")
            print(f"   用时: {result.get('search_time_seconds')} 秒")
            
            for i, doc in enumerate(result.get('results', []), 1):
                print(f"   {i}. {doc.get('title')} (评分: {doc.get('score', 0):.2f})")
            return True
        else:
            print(f"❌ 搜索失败: HTTP {response.status_code}")
            try:
                error_info = response.json()
                print(f"   错误: {error_info.get('error')}")
            except:
                pass
            return False
    except Exception as e:
        print(f"❌ 搜索请求失败: {e}")
        return False

def test_stats():
    """测试统计接口"""
    try:
        response = requests.get(f"{BASE_URL}/stats", timeout=5)
        if response.status_code == 200:
            data = response.json()
            stats = data.get('statistics', {})
            print("✅ 统计信息获取成功:")
            print(f"   文档数: {stats.get('documents_count')}")
            print(f"   词汇量: {stats.get('vocabulary_size')}")
            print(f"   平均长度: {stats.get('average_document_length')}")
            return True
        else:
            print(f"❌ 统计信息获取失败: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 统计请求失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🧪 中文BM25检索服务API测试")
    print("=" * 40)
    print(f"测试服务器: {BASE_URL}")
    print()
    
    # 等待服务启动
    print("⏳ 等待服务启动...")
    time.sleep(2)
    
    # 测试健康检查
    print("1. 测试健康检查接口")
    health_ok = test_health()
    print()
    
    if not health_ok:
        print("❌ 服务未就绪，请检查:")
        print("   1. 确保运行了: python api_server.py")
        print("   2. 检查端口5002是否被占用")
        print("   3. 确保索引已构建")
        return
    
    # 测试搜索
    print("2. 测试搜索接口")
    test_queries = ["猪肝", "儿童套餐", "安全标准"]
    for query in test_queries:
        test_search(query, limit=1)
        time.sleep(0.5)
    print()
    
    # 测试统计
    print("3. 测试统计接口")
    test_stats()
    print()
    
    print("=" * 40)
    print("🎉 API测试完成!")
    print("\n📖 API调用示例:")
    print(f"curl -X GET '{BASE_URL}/health'")
    print(f"curl -X POST '{BASE_URL}/search' \\")
    print("  -H 'Content-Type: application/json' \\")
    print("  -d '{\"query\":\"猪肝\",\"limit\":3}'")

if __name__ == "__main__":
    main()
