#!/usr/bin/env python3
"""
中文BM25检索服务 - 生产级RESTful API
支持跨域请求，适合其他服务调用
"""

from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from chinese_processor import ChineseDocumentProcessor
from chinese_bm25_search import ChineseBM25Search
from config import ChineseConfig
import logging
import traceback
from datetime import datetime
import os

# 创建Flask应用
app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 全局变量
search_engine = None
last_indexed = None

# 在模块导入时立即初始化搜索引擎
def initialize_search_engine():
    """初始化搜索引擎"""
    global search_engine, last_indexed
    
    try:
        processor = ChineseDocumentProcessor()
        
        # 检查索引是否存在
        if (ChineseConfig.INDEX_DIR / 'chinese_documents.json').exists():
            logger.info("加载现有索引...")
            document_index, inverted_index = processor.load_index(ChineseConfig.INDEX_DIR)
            search_engine = ChineseBM25Search(document_index, inverted_index)
            last_indexed = datetime.now()
            logger.info(f"搜索引擎初始化成功: {search_engine.num_documents} 文档")
            return True
        else:
            logger.warning("索引不存在，需要先构建索引")
            return False
            
    except Exception as e:
        logger.error(f"搜索引擎初始化失败: {e}")
        return False

# 在模块导入时执行初始化
initialize_search_engine()

# ==================== API 端点 ====================

@app.route('/', methods=['GET'])
def api_documentation():
    """API文档和状态"""
    return jsonify({
        "service": "中文BM25文档检索服务",
        "version": "1.0.0",
        "status": "运行中" if search_engine else "需要初始化",
        "endpoints": {
            "GET /": "API文档",
            "GET /health": "健康检查",
            "GET /search": "搜索文档",
            "GET /stats": "系统统计",
            "POST /build_index": "重建索引"
        },
        "search_examples": [
            "/search?query=猪肝&limit=3",
            "/search?query=儿童套餐&limit=2",
            "/search?query=安全标准&limit=5"
        ],
        "documents_indexed": search_engine.num_documents if search_engine else 0,
        "vocabulary_size": len(search_engine.inverted_index) if search_engine else 0,
        "last_updated": last_indexed.isoformat() if last_indexed else None
    })

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    status = "healthy" if search_engine else "unhealthy"
    
    return jsonify({
        "status": status,
        "service": "Chinese BM25 Retrieval Service",
        "timestamp": datetime.now().isoformat(),
        "search_engine_ready": search_engine is not None,
        "documents_count": search_engine.num_documents if search_engine else 0,
        "vocabulary_size": len(search_engine.inverted_index) if search_engine else 0,
        "last_indexed": last_indexed.isoformat() if last_indexed else None,
        "api_version": "1.0.0"
    }), 200 if search_engine else 503

@app.route('/search', methods=['GET', 'POST'])
def search_documents():
    """搜索文档接口"""
    if not search_engine:
        return jsonify({
            "error": "搜索引擎未初始化",
            "message": "请先调用 POST /build_index 构建索引",
            "code": "ENGINE_NOT_READY"
        }), 503
    
    try:
        # 获取参数
        if request.method == 'POST':
            data = request.get_json() or {}
            query = data.get('query', '')
            limit = data.get('limit', 10)
            include_snippets = data.get('include_snippets', True)
        else:
            query = request.args.get('query', '')
            limit = int(request.args.get('limit', 10))
            include_snippets = request.args.get('snippets', 'true').lower() == 'true'
        
        # 验证参数
        if not query.strip():
            return jsonify({
                "error": "查询参数不能为空",
                "message": "请提供query参数",
                "example": "/search?query=猪肝"
            }), 400
        
        limit = min(max(1, limit), 50)  # 限制在1-50之间
        
        # 执行搜索
        start_time = datetime.now()
        results = search_engine.search(query, limit)
        search_time = (datetime.now() - start_time).total_seconds()
        
        # 添加文档片段和标题匹配信息
        if include_snippets and results:
            for result in results:
                try:
                    result['snippet'] = search_engine.get_chinese_snippet(
                        result['path'], query, 0
                    )
                except Exception:
                    result['snippet'] = "无法获取片段"
                
                # 添加标题匹配详细信息
                if 'title_bonus' in result:
                    result['title_match_info'] = {
                        'base_score': round(result.get('base_score', 0), 3),
                        'title_bonus': round(result.get('title_bonus', 0), 3),
                        'total_score': round(result.get('score', 0), 3),
                        'title_match_level': _get_title_match_level(result.get('title_bonus', 0))
                    }
        
        return jsonify({
            "success": True,
            "query": query,
            "results_count": len(results),
            "search_time_seconds": round(search_time, 4),
            "results": results,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"搜索失败: {e}")
        return jsonify({
            "error": "搜索过程中发生错误",
            "message": str(e),
            "code": "SEARCH_ERROR"
        }), 500

@app.route('/stats', methods=['GET'])
def get_statistics():
    """获取系统统计信息"""
    if not search_engine:
        return jsonify({
            "error": "搜索引擎未初始化",
            "code": "ENGINE_NOT_READY"
        }), 503
    
    try:
        # 计算统计信息
        total_chars = sum(
            doc.get('chinese_chars', 0) 
            for doc in search_engine.document_index.values()
        )
        
        # 词频统计
        term_frequencies = {}
        for term, docs in search_engine.inverted_index.items():
            term_frequencies[term] = sum(freq for _, freq in docs)
        
        top_terms = sorted(term_frequencies.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return jsonify({
            "success": True,
            "statistics": {
                "documents_count": search_engine.num_documents,
                "vocabulary_size": len(search_engine.inverted_index),
                "average_document_length": round(search_engine.avg_doc_length, 2),
                "total_chinese_characters": total_chars,
                "bm25_parameters": {
                    "k1": search_engine.k1,
                    "b": search_engine.b
                },
                "top_terms": [{"term": term, "frequency": freq} for term, freq in top_terms],
                "last_indexed": last_indexed.isoformat() if last_indexed else None
            },
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"获取统计信息失败: {e}")
        return jsonify({
            "error": "获取统计信息失败",
            "message": str(e)
        }), 500

@app.route('/build_index', methods=['POST'])
def rebuild_index():
    """重建搜索索引"""
    global search_engine, last_indexed
    
    try:
        processor = ChineseDocumentProcessor()
        
        # 查找文档
        documents = processor.find_documents(ChineseConfig.DOCUMENTS_DIR)
        
        if not documents:
            return jsonify({
                "error": "未找到文档",
                "message": f"在 {ChineseConfig.DOCUMENTS_DIR} 中未找到支持的文档",
                "supported_extensions": ChineseConfig.SUPPORTED_EXTENSIONS
            }), 400
        
        # 处理文档
        logger.info(f"开始处理 {len(documents)} 个文档...")
        document_index, inverted_index = processor.process_documents(documents)
        
        if not document_index:
            return jsonify({
                "error": "文档处理失败",
                "message": "没有有效的文档可以处理"
            }), 400
        
        # 保存索引
        processor.save_index(document_index, inverted_index, ChineseConfig.INDEX_DIR)
        
        # 重新初始化搜索引擎
        search_engine = ChineseBM25Search(document_index, inverted_index)
        last_indexed = datetime.now()
        
        logger.info("索引重建完成")
        
        return jsonify({
            "success": True,
            "message": "索引重建成功",
            "documents_indexed": len(document_index),
            "vocabulary_size": len(inverted_index),
            "rebuild_time": last_indexed.isoformat()
        })
        
    except Exception as e:
        logger.error(f"重建索引失败: {e}")
        return jsonify({
            "error": "重建索引失败",
            "message": str(e),
            "code": "INDEX_BUILD_ERROR"
        }), 500

@app.route('/term/<term>', methods=['GET'])
def get_term_info(term):
    """获取词汇详细信息"""
    if not search_engine:
        return jsonify({
            "error": "搜索引擎未初始化",
            "code": "ENGINE_NOT_READY"
        }), 503
    
    try:
        stats = search_engine.get_term_statistics(term)
        return jsonify({
            "success": True,
            "term_info": stats,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            "error": "获取词汇信息失败",
            "message": str(e)
        }), 500

# ==================== 辅助函数 ====================

def _get_title_match_level(title_bonus: float) -> str:
    """根据标题匹配加分返回匹配级别描述"""
    if title_bonus >= 10.0:
        return "完全匹配"
    elif title_bonus >= 8.0:
        return "高度匹配"
    elif title_bonus >= 6.0:
        return "良好匹配"
    elif title_bonus >= 4.0:
        return "部分匹配"
    elif title_bonus >= 2.0:
        return "轻微匹配"
    else:
        return "无匹配"

# ==================== 错误处理 ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "接口不存在",
        "message": "请查看 GET / 获取可用接口列表",
        "code": "NOT_FOUND"
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "error": "内部服务器错误",
        "message": "请稍后重试或联系管理员",
        "code": "INTERNAL_ERROR"
    }), 500

# ==================== 启动服务 ====================

def start_server():
    """启动API服务器"""
    print("🇨🇳 中文BM25检索服务 - RESTful API")
    print("=" * 50)
    print(f"📁 文档目录: {ChineseConfig.DOCUMENTS_DIR}")
    print(f"💾 索引目录: {ChineseConfig.INDEX_DIR}")
    print(f"🌐 服务地址: http://localhost:{ChineseConfig.API_PORT}")
    print(f"📖 API文档: http://localhost:{ChineseConfig.API_PORT}/")
    print("=" * 50)
    
    # 初始化搜索引擎
    if initialize_search_engine():
        print("✅ 搜索引擎就绪!")
    else:
        print("⚠️  搜索引擎未就绪，请调用 POST /build_index")
    
    print("\n🚀 API服务启动中...")
    print("📡 支持跨域请求 (CORS)")
    print("🔄 RESTful接口已准备就绪")
    print("\n按 Ctrl+C 停止服务")
    print("=" * 50)
    
    # 启动Flask服务
    app.run(
        host='0.0.0.0',  # 允许外部访问
        port=ChineseConfig.API_PORT,
        debug=False,
        use_reloader=False,
        threaded=True  # 支持并发请求
    )

if __name__ == '__main__':
    start_server()
