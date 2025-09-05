from flask import Flask, request, jsonify
from pathlib import Path
import traceback
from datetime import datetime
import re
from chinese_processor import ChineseDocumentProcessor
from chinese_bm25_search import ChineseBM25Search
from config import ChineseConfig

app = Flask(__name__)

# Global variables
search_engine = None
last_indexed = None

def initialize_chinese_search_engine():
    """Initialize Chinese search engine"""
    global search_engine, last_indexed
    
    try:
        ChineseConfig.create_directories()
        processor = ChineseDocumentProcessor()
        
        # Check if Chinese index exists
        index_files_exist = (
            (ChineseConfig.INDEX_DIR / 'chinese_documents.json').exists() and
            (ChineseConfig.INDEX_DIR / 'chinese_inverted_index.pkl').exists()
        )
        
        if index_files_exist:
            print("📚 Loading existing Chinese index...")
            document_index, inverted_index = processor.load_index(ChineseConfig.INDEX_DIR)
            search_engine = ChineseBM25Search(document_index, inverted_index)
            last_indexed = datetime.now()
            print("✅ Chinese search engine ready!")
        else:
            print("⚠️  No Chinese index found. Please build index first using /build_chinese_index")
            
    except Exception as e:
        print(f"❌ Error initializing Chinese search engine: {e}")
        traceback.print_exc()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check for Chinese service"""
    return jsonify({
        'status': 'healthy',
        'service': 'Chinese BM25 Retrieval',
        'search_engine_loaded': search_engine is not None,
        'last_indexed': last_indexed.isoformat() if last_indexed else None,
        'documents_dir': str(ChineseConfig.DOCUMENTS_DIR),
        'language': 'Chinese (Simplified)'
    })

@app.route('/build_chinese_index', methods=['POST'])
def build_chinese_index():
    """Build Chinese document index from laicai_document folder"""
    global search_engine, last_indexed
    
    try:
        processor = ChineseDocumentProcessor()
        
        print(f"🔍 Scanning Chinese documents in: {ChineseConfig.DOCUMENTS_DIR}")
        
        # Check if directory exists
        if not ChineseConfig.DOCUMENTS_DIR.exists():
            return jsonify({
                'error': f'Documents directory not found: {ChineseConfig.DOCUMENTS_DIR}',
                'suggestion': 'Please check the path in config.py'
            }), 400
        
        # Find documents
        documents = processor.find_documents(ChineseConfig.DOCUMENTS_DIR)
        
        if not documents:
            return jsonify({
                'error': 'No Chinese documents found',
                'search_path': str(ChineseConfig.DOCUMENTS_DIR),
                'supported_extensions': ChineseConfig.SUPPORTED_EXTENSIONS
            }), 400
        
        # Process documents
        document_index, inverted_index = processor.process_documents(documents)
        
        if not document_index:
            return jsonify({
                'error': 'No valid Chinese documents could be processed'
            }), 400
        
        # Save index
        processor.save_index(document_index, inverted_index, ChineseConfig.INDEX_DIR)
        
        # Initialize search engine
        search_engine = ChineseBM25Search(document_index, inverted_index)
        last_indexed = datetime.now()
        
        return jsonify({
            'status': 'success',
            'message': '中文索引构建成功 (Chinese index built successfully)',
            'documents_indexed': len(document_index),
            'vocabulary_size': len(inverted_index),
            'last_indexed': last_indexed.isoformat(),
            'chinese_optimizations': [
                'jieba分词 (jieba segmentation)',
                '中文停用词过滤 (Chinese stop words filtering)',
                '词性标注 (Part-of-speech tagging)',
                'BM25参数优化 (Optimized BM25 parameters)'
            ]
        })
        
    except Exception as e:
        error_msg = f"Chinese index building error: {e}"
        print(error_msg)
        traceback.print_exc()
        return jsonify({'error': error_msg}), 500

@app.route('/search_chinese', methods=['GET', 'POST'])
def search_chinese():
    """Search Chinese documents"""
    if search_engine is None:
        return jsonify({
            'error': '中文搜索引擎未初始化 (Chinese search engine not initialized)',
            'suggestion': 'POST to /build_chinese_index to create the index'
        }), 400
    
    try:
        # Get search parameters
        if request.method == 'POST':
            data = request.get_json() or {}
            query = data.get('query', '')
            limit = data.get('limit', ChineseConfig.DEFAULT_RESULTS_LIMIT)
            include_snippets = data.get('include_snippets', True)
            analyze_query = data.get('analyze_query', False)
        else:
            query = request.args.get('query', '')
            limit = int(request.args.get('limit', ChineseConfig.DEFAULT_RESULTS_LIMIT))
            include_snippets = request.args.get('include_snippets', 'true').lower() == 'true'
            analyze_query = request.args.get('analyze_query', 'false').lower() == 'true'
        
        if not query.strip():
            return jsonify({'error': '查询参数不能为空 (Query parameter required)'}), 400
        
        # Perform Chinese search
        results = search_engine.search(query, limit)
        
        # Add Chinese snippets if requested
        if include_snippets:
            for result in results:
                result['snippet'] = search_engine.get_chinese_snippet(
                    result['path'], query
                )
        
        response = {
            'query': query,
            'total_results': len(results),
            'limit': limit,
            'results': results,
            'search_time': datetime.now().isoformat()
        }
        
        # Add query analysis if requested
        if analyze_query:
            response['query_analysis'] = search_engine.analyze_query(query)
        
        return jsonify(response)
        
    except Exception as e:
        error_msg = f"Chinese search error: {e}"
        print(error_msg)
        traceback.print_exc()
        return jsonify({'error': error_msg}), 500

@app.route('/chinese_term_stats/<term>', methods=['GET'])
def chinese_term_statistics(term):
    """Get statistics for a Chinese term"""
    if search_engine is None:
        return jsonify({'error': '搜索引擎未初始化'}), 400
    
    try:
        stats = search_engine.get_term_statistics(term)
        return jsonify(stats)
        
    except Exception as e:
        return jsonify({'error': f"获取词汇统计时出错: {e}"}), 500

@app.route('/chinese_similar/<int:doc_id>', methods=['GET'])
def chinese_similar_documents(doc_id):
    """Find similar Chinese documents"""
    if search_engine is None:
        return jsonify({'error': '搜索引擎未初始化'}), 400
    
    try:
        limit = int(request.args.get('limit', 5))
        similar_docs = search_engine.get_similar_documents(doc_id, limit)
        
        return jsonify({
            'doc_id': doc_id,
            'similar_documents': similar_docs,
            'algorithm': 'Chinese term overlap analysis'
        })
        
    except Exception as e:
        return jsonify({'error': f"查找相似文档时出错: {e}"}), 500

@app.route('/chinese_document/<int:doc_id>', methods=['GET'])
def get_chinese_document(doc_id):
    """Get Chinese document information"""
    if search_engine is None:
        return jsonify({'error': '搜索引擎未初始化'}), 400
    
    try:
        if doc_id not in search_engine.document_index:
            return jsonify({'error': '文档未找到'}), 404
        
        doc_data = search_engine.document_index[doc_id]
        
        result = {
            'doc_id': doc_id,
            'path': doc_data['path'],
            'title': doc_data['title'],
            'length': doc_data['length'],
            'chinese_chars': doc_data.get('chinese_chars', 0),
            'total_chars': doc_data.get('total_chars', 0),
            'top_terms': dict(doc_data['term_frequencies'].most_common(10))
        }
        
        # Include content if requested
        include_content = request.args.get('include_content', 'false').lower() == 'true'
        if include_content:
            try:
                processor = ChineseDocumentProcessor()
                content = processor._read_file_with_encoding(Path(doc_data['path']))
                result['content'] = content
            except Exception as e:
                result['content_error'] = str(e)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': f"获取文档信息时出错: {e}"}), 500

@app.route('/chinese_stats', methods=['GET'])
def get_chinese_stats():
    """Get Chinese search engine statistics"""
    if search_engine is None:
        return jsonify({'error': '搜索引擎未初始化'}), 400
    
    try:
        # Calculate additional Chinese-specific statistics
        total_chinese_chars = sum(
            doc.get('chinese_chars', 0) 
            for doc in search_engine.document_index.values()
        )
        
        stats = {
            'service': 'Chinese BM25 Document Retrieval',
            'total_documents': search_engine.num_documents,
            'vocabulary_size': len(search_engine.inverted_index),
            'average_document_length': round(search_engine.avg_doc_length, 2),
            'total_chinese_characters': total_chinese_chars,
            'last_indexed': last_indexed.isoformat() if last_indexed else None,
            'chinese_bm25_parameters': {
                'k1': search_engine.k1,
                'b': search_engine.b,
                'optimization': 'Tuned for Chinese text characteristics'
            },
            'processing_features': {
                'segmentation': 'jieba with HMM',
                'pos_tagging': 'Enabled' if ChineseConfig.ENABLE_POS_FILTERING else 'Disabled',
                'custom_dictionary': 'Auto-generated from documents',
                'stop_words': 'Chinese stop words',
                'encoding_support': ['UTF-8', 'GBK', 'GB2312', 'Big5']
            },
            'config': {
                'max_results_limit': ChineseConfig.MAX_RESULTS_LIMIT,
                'default_results_limit': ChineseConfig.DEFAULT_RESULTS_LIMIT,
                'documents_directory': str(ChineseConfig.DOCUMENTS_DIR)
            }
        }
        
        return jsonify(stats)
        
    except Exception as e:
        return jsonify({'error': f"获取统计信息时出错: {e}"}), 500

@app.route('/', methods=['GET'])
def chinese_api_docs():
    """Chinese API documentation"""
    docs = {
        'title': '中文BM25文档检索服务 (Chinese BM25 Document Retrieval Service)',
        'description': '专为中文文档优化的搜索服务 (Search service optimized for Chinese documents)',
        'language': 'Chinese (Simplified)',
        'optimization_features': [
            'jieba中文分词 (jieba Chinese segmentation)',
            '中文停用词过滤 (Chinese stop words filtering)', 
            '词性标注 (Part-of-speech tagging)',
            'BM25参数优化 (Optimized BM25 parameters)',
            '多编码支持 (Multiple encoding support)'
        ],
        'endpoints': {
            'GET /': 'API文档 (This documentation)',
            'GET /health': '健康检查 (Health check)',
            'POST /build_chinese_index': '构建中文索引 (Build Chinese index)',
            'GET/POST /search_chinese': '搜索中文文档 (Search Chinese documents)',
            'GET /chinese_term_stats/<term>': '中文词汇统计 (Chinese term statistics)',
            'GET /chinese_similar/<doc_id>': '查找相似文档 (Find similar documents)',
            'GET /chinese_document/<doc_id>': '获取文档信息 (Get document info)',
            'GET /chinese_stats': '搜索引擎统计 (Search engine statistics)'
        },
        'example_search': {
            'url': '/search_chinese',
            'method': 'POST',
            'body': {
                'query': '猪肝 菜谱',
                'limit': 10,
                'include_snippets': True,
                'analyze_query': True
            }
        },
        'sample_queries': [
            '猪肝制作方法',
            '儿童套餐',
            '安全标准',
            '人事制度',
            '汤圆做法'
        ]
    }
    return jsonify(docs)

if __name__ == '__main__':
    print("🇨🇳 启动中文BM25检索服务... (Starting Chinese BM25 Retrieval Service...)")
    print(f"📁 文档目录: {ChineseConfig.DOCUMENTS_DIR}")
    print(f"💾 索引目录: {ChineseConfig.INDEX_DIR}")
    print(f"🌐 服务地址: http://{ChineseConfig.API_HOST}:{ChineseConfig.API_PORT}")
    print(f"📖 API文档: http://localhost:{ChineseConfig.API_PORT}/")
    print("=" * 50)
    
    # Initialize search engine
    print("🔧 初始化搜索引擎...")
    initialize_chinese_search_engine()
    
    if search_engine:
        print("✅ 搜索引擎初始化成功！")
        print(f"   - 文档数量: {search_engine.num_documents}")
        print(f"   - 词汇量: {len(search_engine.inverted_index):,}")
    else:
        print("⚠️  搜索引擎未初始化，请先构建索引")
    
    print("\n🚀 启动Flask服务器...")
    print("按 Ctrl+C 停止服务")
    print("=" * 50)
    
    try:
        # Start Flask app
        app.run(
            host=ChineseConfig.API_HOST,
            port=ChineseConfig.API_PORT,
            debug=ChineseConfig.DEBUG,
            use_reloader=False  # 避免重复初始化
        )
    except Exception as e:
        print(f"❌ 启动服务失败: {e}")
        print("💡 提示: 请检查端口是否被占用或权限问题")
