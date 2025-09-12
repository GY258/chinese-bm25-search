#!/usr/bin/env python3
"""
演示测试 - 展示服务功能
"""

import requests
import json
import time
from datetime import datetime

def demo_test():
    """演示测试功能"""
    base_url = "http://localhost:5003"
    
    print("🧪 中文BM25检索服务演示测试")
    print("=" * 50)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"服务地址: {base_url}")
    print("=" * 50)
    
    # 检查服务状态
    print("\n🔍 检查服务状态...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ 服务运行正常!")
            print(f"   状态: {data.get('status')}")
            print(f"   文档数: {data.get('documents_count')}")
            print(f"   词汇量: {data.get('vocabulary_size')}")
        else:
            print(f"❌ 服务异常: HTTP {response.status_code}")
            return
    except Exception as e:
        print(f"❌ 无法连接到服务: {e}")
        print("请确保服务正在运行:")
        print("  1. 运行: ./deploy.sh")
        print("  2. 等待服务启动完成")
        return
    
    # 演示搜索功能
    print("\n🔍 搜索功能演示")
    print("-" * 30)
    
    demo_queries = [
        # "猪肝",
        # "儿童套餐", 
        # "安全标准",
        # "汤圆",
        # "人事制度",
        "藕汤",
        "筒骨wei藕汤",
        "铫子筒骨煨藕汤产品标准",
        "铫子筒骨煨藕汤",
        "筒骨煨藕汤",
        "藕汤的做法"
    ]
    
    for query in demo_queries:
        print(f"\n搜索: '{query}'")
        try:
            start_time = time.time()
            response = requests.get(f"{base_url}/search?query={query}&limit=3", timeout=10)
            end_time = time.time()
            
            if response.status_code == 200:
                data = response.json()
                results = data.get('results', [])
                search_time = data.get('search_time_seconds', end_time - start_time)
                
                print(f"   ✅ 找到 {len(results)} 个结果 (用时: {search_time:.3f}秒)")
                
                for i, result in enumerate(results, 1):
                    title = result.get('title', 'N/A')
                    score = result.get('score', 0)
                    print(f"   {i}. {title} (评分: {score:.2f})")
                    
                    # 显示文档片段
                    snippet = result.get('snippet', '')
                    if snippet:
                        print(f"      片段: {snippet[:100]}...")
            else:
                print(f"   ❌ 搜索失败: HTTP {response.status_code}")
        except Exception as e:
            print(f"   ❌ 搜索异常: {e}")
    
    # 演示POST搜索
    print(f"\n📝 POST搜索演示")
    print("-" * 30)
    try:
        data = {
            "query": "操作流程 安全",
            "limit": 2,
            "include_snippets": True
        }
        response = requests.post(f"{base_url}/search", json=data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ POST搜索成功: '{result.get('query')}'")
            print(f"   找到 {result.get('results_count')} 个结果")
            
            for i, doc in enumerate(result.get('results', []), 1):
                print(f"   {i}. {doc.get('title')} (评分: {doc.get('score', 0):.2f})")
        else:
            print(f"❌ POST搜索失败: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ POST搜索异常: {e}")
    
    # 演示统计信息
    print(f"\n📊 统计信息演示")
    print("-" * 30)
    try:
        response = requests.get(f"{base_url}/stats", timeout=5)
        if response.status_code == 200:
            data = response.json()
            stats = data.get('statistics', {})
            
            print("✅ 系统统计信息:")
            print(f"   文档总数: {stats.get('documents_count')}")
            print(f"   词汇总量: {stats.get('vocabulary_size')}")
            print(f"   平均文档长度: {stats.get('average_document_length')}")
            
            # 显示热门词汇
            top_terms = stats.get('top_terms', [])
            if top_terms:
                print("   热门词汇:")
                for term_info in top_terms[:5]:
                    term = term_info.get('term')
                    freq = term_info.get('frequency')
                    print(f"     - {term}: {freq} 次")
        else:
            print(f"❌ 统计信息获取失败: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ 统计信息异常: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 演示测试完成!")
    print("\n📖 API使用示例:")
    print(f"# 健康检查")
    print(f"curl -X GET '{base_url}/health'")
    print(f"\n# 基本搜索")
    print(f"curl -X GET '{base_url}/search?query=猪肝&limit=3'")
    print(f"\n# POST搜索")
    print(f"curl -X POST '{base_url}/search' \\")
    print(f"  -H 'Content-Type: application/json' \\")
    print(f"  -d '{{\"query\":\"儿童套餐\",\"limit\":2}}'")
    print(f"\n# 统计信息")
    print(f"curl -X GET '{base_url}/stats'")

if __name__ == "__main__":
    demo_test()