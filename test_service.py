#!/usr/bin/env python3
"""
简单的中文搜索服务测试工具
"""

from chinese_processor import ChineseDocumentProcessor
from chinese_bm25_search import ChineseBM25Search
from config import ChineseConfig
import json

def test_chinese_search():
    """测试中文搜索功能"""
    print("🇨🇳 中文搜索服务测试")
    print("=" * 40)
    
    try:
        # 初始化处理器
        processor = ChineseDocumentProcessor()
        
        # 加载索引
        print("📚 加载索引...")
        document_index, inverted_index = processor.load_index(ChineseConfig.INDEX_DIR)
        
        # 初始化搜索引擎
        search_engine = ChineseBM25Search(document_index, inverted_index)
        
        print(f"✅ 搜索引擎加载成功!")
        print(f"   文档数: {len(document_index)}")
        print(f"   词汇量: {len(inverted_index):,}")
        
        # 测试搜索
        test_queries = ["猪肝", "儿童套餐", "安全标准", "汤圆", "人事制度"]
        
        for query in test_queries:
            print(f"\n🔍 搜索: '{query}'")
            results = search_engine.search(query, limit=2)
            
            if results:
                for i, result in enumerate(results, 1):
                    print(f"  {i}. {result['title']} (评分: {result['score']:.2f})")
            else:
                print("  ❌ 无结果")
        
        print("\n" + "=" * 40)
        print("✅ 测试完成! 搜索功能正常工作")
        
        # 返回搜索引擎供API使用
        return search_engine
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def start_simple_api(search_engine):
    """启动简化的API服务"""
    from flask import Flask, request, jsonify
    
    app = Flask(__name__)
    
    @app.route('/health')
    def health():
        return jsonify({
            'status': 'healthy',
            'documents': search_engine.num_documents if search_engine else 0,
            'vocabulary': len(search_engine.inverted_index) if search_engine else 0
        })
    
    @app.route('/search')
    def search():
        query = request.args.get('query', '')
        limit = int(request.args.get('limit', 5))
        
        if not query:
            return jsonify({'error': '请提供查询参数'})
        
        if search_engine:
            results = search_engine.search(query, limit)
            return jsonify({
                'query': query,
                'results': results,
                'total': len(results)
            })
        else:
            return jsonify({'error': '搜索引擎未初始化'})
    
    @app.route('/')
    def index():
        return jsonify({
            'title': '中文BM25搜索服务',
            'endpoints': {
                '/health': '健康检查',
                '/search?query=<查询词>&limit=<数量>': '搜索文档'
            },
            'examples': [
                '/search?query=猪肝&limit=3',
                '/search?query=儿童套餐&limit=2'
            ]
        })
    
    print(f"\n🚀 启动简化API服务...")
    print(f"🌐 地址: http://localhost:{ChineseConfig.API_PORT}")
    print("按 Ctrl+C 停止")
    
    try:
        app.run(
            host='127.0.0.1',  # 只绑定本地
            port=ChineseConfig.API_PORT,
            debug=False,  # 关闭调试模式
            use_reloader=False
        )
    except KeyboardInterrupt:
        print("\n👋 服务已停止")
    except Exception as e:
        print(f"❌ 服务启动失败: {e}")

if __name__ == '__main__':
    # 测试搜索功能
    search_engine = test_chinese_search()
    
    if search_engine:
        # 启动API服务
        start_simple_api(search_engine)
    else:
        print("❌ 无法启动API服务")
