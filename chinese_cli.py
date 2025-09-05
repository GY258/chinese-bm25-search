#!/usr/bin/env python3
"""
中文BM25检索服务命令行工具 (Chinese BM25 Retrieval CLI)
"""

import click
import json
from pathlib import Path
from chinese_processor import ChineseDocumentProcessor
from chinese_bm25_search import ChineseBM25Search
from config import ChineseConfig

@click.group()
def cli():
    """中文文档检索CLI工具 (Chinese Document Retrieval CLI)"""
    pass

@cli.command()
def build_index():
    """构建中文文档索引 (Build Chinese document index)"""
    try:
        ChineseConfig.create_directories()
        processor = ChineseDocumentProcessor()
        
        print(f"🔍 扫描中文文档: {ChineseConfig.DOCUMENTS_DIR}")
        
        if not ChineseConfig.DOCUMENTS_DIR.exists():
            print(f"❌ 文档目录不存在: {ChineseConfig.DOCUMENTS_DIR}")
            return
        
        documents = processor.find_documents(ChineseConfig.DOCUMENTS_DIR)
        
        if not documents:
            print(f"❌ 未找到文档在: {ChineseConfig.DOCUMENTS_DIR}")
            print(f"支持的扩展名: {ChineseConfig.SUPPORTED_EXTENSIONS}")
            return
        
        print(f"📄 找到 {len(documents)} 个文档")
        
        # Process documents
        document_index, inverted_index = processor.process_documents(documents)
        
        if not document_index:
            print("❌ 没有有效文档可以处理")
            return
        
        # Save index
        processor.save_index(document_index, inverted_index, ChineseConfig.INDEX_DIR)
        
        print(f"\n✅ 中文索引构建成功!")
        print(f"   索引文档数: {len(document_index)}")
        print(f"   词汇量: {len(inverted_index):,}")
        print(f"   索引保存到: {ChineseConfig.INDEX_DIR}")
        
    except Exception as e:
        print(f"❌ 构建索引时出错: {e}")

@cli.command()
@click.argument('query')
@click.option('--limit', default=10, help='最大结果数量')
@click.option('--snippets', is_flag=True, help='包含文档片段')
def search(query, limit, snippets):
    """搜索中文文档 (Search Chinese documents)"""
    try:
        processor = ChineseDocumentProcessor()
        
        if not (ChineseConfig.INDEX_DIR / 'chinese_documents.json').exists():
            print("❌ 索引不存在，请先使用 'build-index' 命令构建索引")
            return
        
        document_index, inverted_index = processor.load_index(ChineseConfig.INDEX_DIR)
        search_engine = ChineseBM25Search(document_index, inverted_index)
        
        # Perform search
        results = search_engine.search(query, limit)
        
        if not results:
            print(f"❌ 没有找到包含 '{query}' 的结果")
            return
        
        print(f"\n🔍 搜索结果: '{query}'")
        print(f"找到 {len(results)} 个结果\n")
        
        for i, result in enumerate(results, 1):
            print(f"{i}. {result['title']}")
            print(f"   评分: {result['score']:.4f} ({result['relevance']})")
            print(f"   路径: {result['path']}")
            print(f"   长度: {result['length']} 个词")
            print(f"   中文字符: {result.get('chinese_chars', 0)} 个")
            
            if snippets:
                snippet = search_engine.get_chinese_snippet(result['path'], query)
                print(f"   片段: {snippet}")
            
            print()
    
    except Exception as e:
        print(f"❌ 搜索时出错: {e}")

@cli.command()
@click.argument('term')
def term_stats(term):
    """获取中文词汇统计 (Get Chinese term statistics)"""
    try:
        processor = ChineseDocumentProcessor()
        
        if not (ChineseConfig.INDEX_DIR / 'chinese_documents.json').exists():
            print("❌ 索引不存在，请先构建索引")
            return
        
        document_index, inverted_index = processor.load_index(ChineseConfig.INDEX_DIR)
        search_engine = ChineseBM25Search(document_index, inverted_index)
        
        stats = search_engine.get_term_statistics(term)
        
        if 'error' in stats:
            print(f"❌ {stats['error']}")
            return
        
        if stats.get('document_frequency', 0) == 0:
            print(f"❌ 词汇 '{term}' 不在索引中")
            return
        
        print(f"\n📊 词汇统计: '{stats['term']}'")
        print(f"文档频率: {stats['document_frequency']}")
        print(f"总频率: {stats['total_frequency']}")
        print(f"IDF评分: {stats['idf_score']}")
        print(f"覆盖率: {stats['coverage']}")
        
        if 'documents' in stats and stats['documents']:
            print(f"\n包含此词的前5个文档:")
            for doc_id, freq in stats['documents']:
                doc_data = document_index[doc_id]
                print(f"  {doc_data['title']} (频率: {freq})")
    
    except Exception as e:
        print(f"❌ 获取词汇统计时出错: {e}")

@cli.command()
def stats():
    """显示搜索引擎统计信息 (Show search engine statistics)"""
    try:
        processor = ChineseDocumentProcessor()
        
        if not (ChineseConfig.INDEX_DIR / 'chinese_documents.json').exists():
            print("❌ 索引不存在，请先构建索引")
            return
        
        document_index, inverted_index = processor.load_index(ChineseConfig.INDEX_DIR)
        search_engine = ChineseBM25Search(document_index, inverted_index)
        
        total_chinese_chars = sum(
            doc.get('chinese_chars', 0) 
            for doc in document_index.values()
        )
        
        print(f"\n📊 中文搜索引擎统计")
        print(f"总文档数: {search_engine.num_documents}")
        print(f"词汇量: {len(search_engine.inverted_index):,}")
        print(f"平均文档长度: {search_engine.avg_doc_length:.1f} 个词")
        print(f"总中文字符数: {total_chinese_chars:,}")
        print(f"BM25参数: k1={search_engine.k1}, b={search_engine.b}")
        print(f"索引位置: {ChineseConfig.INDEX_DIR}")
        
        # Document length distribution
        lengths = [doc['length'] for doc in document_index.values()]
        if lengths:
            lengths.sort()
            print(f"\n文档长度分布:")
            print(f"  最短: {min(lengths)} 个词")
            print(f"  最长: {max(lengths)} 个词")
            print(f"  中位数: {lengths[len(lengths)//2]} 个词")
        
        # Most frequent terms
        term_frequencies = {}
        for term, docs in inverted_index.items():
            term_frequencies[term] = sum(freq for _, freq in docs)
        
        most_common = sorted(term_frequencies.items(), key=lambda x: x[1], reverse=True)[:10]
        
        print(f"\n最常见词汇:")
        for term, freq in most_common:
            print(f"  {term}: {freq}")
    
    except Exception as e:
        print(f"❌ 获取统计信息时出错: {e}")

@cli.command()
@click.argument('doc_id', type=int)
@click.option('--limit', default=5, help='相似文档数量')
def similar(doc_id, limit):
    """查找相似文档 (Find similar documents)"""
    try:
        processor = ChineseDocumentProcessor()
        
        if not (ChineseConfig.INDEX_DIR / 'chinese_documents.json').exists():
            print("❌ 索引不存在，请先构建索引")
            return
        
        document_index, inverted_index = processor.load_index(ChineseConfig.INDEX_DIR)
        search_engine = ChineseBM25Search(document_index, inverted_index)
        
        if doc_id not in document_index:
            print(f"❌ 文档ID {doc_id} 不存在")
            return
        
        similar_docs = search_engine.get_similar_documents(doc_id, limit)
        
        source_doc = document_index[doc_id]
        print(f"\n相似文档: {source_doc['title']}")
        print(f"路径: {source_doc['path']}")
        
        if not similar_docs:
            print("❌ 没有找到相似文档")
            return
        
        print(f"\n找到 {len(similar_docs)} 个相似文档:")
        
        for i, doc in enumerate(similar_docs, 1):
            print(f"{i}. {doc['title']}")
            print(f"   相似度: {doc['similarity_score']:.4f}")
            print(f"   共同词汇: {doc['shared_terms']} 个")
            print(f"   路径: {doc['path']}")
            print()
    
    except Exception as e:
        print(f"❌ 查找相似文档时出错: {e}")

@cli.command()
@click.argument('query')
def analyze(query):
    """分析查询词 (Analyze query)"""
    try:
        processor = ChineseDocumentProcessor()
        
        if not (ChineseConfig.INDEX_DIR / 'chinese_documents.json').exists():
            print("❌ 索引不存在，请先构建索引")
            return
        
        document_index, inverted_index = processor.load_index(ChineseConfig.INDEX_DIR)
        search_engine = ChineseBM25Search(document_index, inverted_index)
        
        analysis = search_engine.analyze_query(query)
        
        print(f"\n🔍 查询分析: '{analysis['original_query']}'")
        print(f"处理后的词汇: {analysis['processed_terms']}")
        print(f"词汇数量: {analysis['term_count']}")
        
        print(f"\n词汇详细分析:")
        for term_info in analysis['term_analysis']:
            print(f"  '{term_info['term']}':")
            print(f"    频率: {term_info['frequency']}")
            print(f"    文档覆盖: {term_info['document_coverage']}")
            print(f"    稀有度: {term_info['rarity_score']}")
    
    except Exception as e:
        print(f"❌ 分析查询时出错: {e}")

if __name__ == '__main__':
    cli()
