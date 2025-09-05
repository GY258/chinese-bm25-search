#!/usr/bin/env python3
"""
简单的中文搜索命令行工具
用法: python search.py "搜索词"
"""

import sys
from chinese_processor import ChineseDocumentProcessor
from chinese_bm25_search import ChineseBM25Search
from config import ChineseConfig

def search_documents(query, limit=5):
    """搜索中文文档"""
    try:
        # 初始化
        processor = ChineseDocumentProcessor()
        
        # 加载索引
        print(f"🔍 搜索: '{query}'")
        document_index, inverted_index = processor.load_index(ChineseConfig.INDEX_DIR)
        search_engine = ChineseBM25Search(document_index, inverted_index)
        
        # 执行搜索
        results = search_engine.search(query, limit)
        
        if not results:
            print("❌ 没有找到相关文档")
            return
        
        print(f"\n✅ 找到 {len(results)} 个结果:\n")
        
        for i, result in enumerate(results, 1):
            print(f"{i}. 📄 {result['title']}")
            print(f"   🔢 评分: {result['score']:.2f} ({result['relevance']})")
            print(f"   📁 路径: {result['path']}")
            print(f"   📝 长度: {result['length']} 词, {result.get('chinese_chars', 0)} 中文字符")
            
            # 获取文档片段
            try:
                snippet = search_engine.get_chinese_snippet(result['path'], query, 150)
                print(f"   📃 片段: {snippet}")
            except:
                pass
            print()
        
    except Exception as e:
        print(f"❌ 搜索失败: {e}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python search.py '搜索词' [数量]")
        print("示例:")
        print("  python search.py '猪肝'")
        print("  python search.py '儿童套餐' 3")
        sys.exit(1)
    
    query = sys.argv[1]
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    
    search_documents(query, limit)
