#!/usr/bin/env python3
"""
测试标题权重功能
验证标题匹配的文档是否能排在更前面
"""

import requests
import json
import time
from datetime import datetime

def test_title_weight():
    """测试标题权重功能"""
    base_url = "http://localhost:5003"
    
    print("🧪 标题权重功能测试")
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
            print(f"   文档数: {data.get('documents_count')}")
        else:
            print(f"❌ 服务异常: HTTP {response.status_code}")
            return
    except Exception as e:
        print(f"❌ 无法连接到服务: {e}")
        return
    
    # 测试标题权重功能
    print("\n🎯 标题权重测试")
    print("-" * 30)
    
    test_queries = [
        "铫子筒骨煨藕汤产品标准",
        "藕汤大使岗",
        "菜品知识",
        "儿童套餐",
        "安全标准"
    ]
    
    for query in test_queries:
        print(f"\n🔍 搜索: '{query}'")
        try:
            response = requests.get(f"{base_url}/search?query={query}&limit=5", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                results = data.get('results', [])
                
                print(f"   ✅ 找到 {len(results)} 个结果")
                
                for i, result in enumerate(results, 1):
                    title = result.get('title', 'N/A')
                    score = result.get('score', 0)
                    base_score = result.get('base_score', 0)
                    title_bonus = result.get('title_bonus', 0)
                    
                    print(f"   {i}. {title}")
                    print(f"      总分: {score:.3f} (基础分: {base_score:.3f} + 标题加分: {title_bonus:.3f})")
                    
                    # 显示标题匹配信息
                    title_match_info = result.get('title_match_info', {})
                    if title_match_info:
                        match_level = title_match_info.get('title_match_level', '无匹配')
                        print(f"      标题匹配: {match_level}")
                    
                    # 检查是否是标题完全匹配
                    if title == query:
                        print(f"      🎯 标题完全匹配!")
                    elif query in title:
                        print(f"      📝 标题包含查询词")
                    
                    print()
            else:
                print(f"   ❌ 搜索失败: HTTP {response.status_code}")
        except Exception as e:
            print(f"   ❌ 搜索异常: {e}")
    
    # 专门测试"铫子筒骨煨藕汤产品标准"
    print("\n🎯 重点测试: 铫子筒骨煨藕汤产品标准")
    print("-" * 50)
    
    query = "铫子筒骨煨藕汤产品标准"
    try:
        response = requests.get(f"{base_url}/search?query={query}&limit=10", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            
            print(f"搜索 '{query}' 的结果:")
            print(f"找到 {len(results)} 个结果\n")
            
            for i, result in enumerate(results, 1):
                title = result.get('title', 'N/A')
                score = result.get('score', 0)
                base_score = result.get('base_score', 0)
                title_bonus = result.get('title_bonus', 0)
                
                print(f"{i}. {title}")
                print(f"   总分: {score:.3f}")
                print(f"   基础分: {base_score:.3f}")
                print(f"   标题加分: {title_bonus:.3f}")
                
                # 显示标题匹配信息
                title_match_info = result.get('title_match_info', {})
                if title_match_info:
                    match_level = title_match_info.get('title_match_level', '无匹配')
                    print(f"   匹配级别: {match_level}")
                
                # 检查是否是目标文档
                if "铫子筒骨煨藕汤产品标准" in title:
                    print(f"   🎯 这是目标文档!")
                    if i == 1:
                        print(f"   ✅ 成功! 目标文档排在第一位")
                    else:
                        print(f"   ⚠️  目标文档排在第 {i} 位")
                
                print()
        else:
            print(f"❌ 搜索失败: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ 搜索异常: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 标题权重测试完成!")
    print("\n📊 测试说明:")
    print("- 标题完全匹配: +10.0 分")
    print("- 高度匹配(80%+): +8.0 分")
    print("- 良好匹配(60%+): +6.0 分")
    print("- 部分匹配(40%+): +4.0 分")
    print("- 轻微匹配(20%+): +2.0 分")
    print("- 子串匹配: +7.0 分")

if __name__ == "__main__":
    test_title_weight()
