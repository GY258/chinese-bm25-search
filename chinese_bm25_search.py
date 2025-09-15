import math
import numpy as np
from collections import Counter, defaultdict
from typing import List, Dict, Tuple, Optional
from chinese_processor import ChineseDocumentProcessor
from config import ChineseConfig

class ChineseBM25Search:
    """
    BM25 search engine optimized for Chinese text
    Uses parameters tuned for Chinese language characteristics
    """
    
    def __init__(self, document_index: Dict, inverted_index: Dict):
        self.document_index = document_index
        self.inverted_index = inverted_index
        self.processor = ChineseDocumentProcessor()
        
        # Calculate document statistics
        self.num_documents = len(document_index)
        self.avg_doc_length = self._calculate_avg_doc_length()
        
        # BM25 parameters optimized for Chinese
        self.k1 = ChineseConfig.K1  # 1.5 - higher for Chinese (less term repetition)
        self.b = ChineseConfig.B    # 0.6 - lower for Chinese (less length penalty)
        
        print(f"🔍 Chinese BM25 Search initialized")
        print(f"   Documents: {self.num_documents}")
        print(f"   Average document length: {self.avg_doc_length:.1f} tokens")
        print(f"   Vocabulary size: {len(self.inverted_index):,}")
        print(f"   BM25 parameters: k1={self.k1}, b={self.b}")
        print(f"   Keyword boosts: {ChineseConfig.KEYWORD_BOOSTS}")
    
    def _calculate_avg_doc_length(self) -> float:
        """Calculate average document length"""
        if not self.document_index:
            return 0.0
        total_length = sum(doc['length'] for doc in self.document_index.values())
        return total_length / len(self.document_index)
    
    def _calculate_idf(self, term: str) -> float:
        """Calculate Inverse Document Frequency with smoothing"""
        if term not in self.inverted_index:
            return 0.0
        
        df = len(self.inverted_index[term])  # Document frequency
        
        # IDF with smoothing: log((N - df + 0.5) / (df + 0.5))
        idf = math.log((self.num_documents - df + 0.5) / (df + 0.5))
        return max(0.0, idf)
    
    def _get_keyword_boost(self, term: str) -> float:
        """Get keyword boost multiplier for important terms"""
        return ChineseConfig.KEYWORD_BOOSTS.get(term, 1.0)
    
    def _calculate_title_match_score(self, query_terms: List[str], doc_title: str) -> float:
        """
        Calculate title match bonus score with enhanced weighting
        Returns higher score for better title matches, especially for important keywords
        """
        if not query_terms or not doc_title:
            return 0.0
        
        # Process title to get tokens
        title_tokens = self.processor.preprocess_text(doc_title)
        if not title_tokens:
            return 0.0
        
        # Calculate match metrics
        query_set = set(query_terms)
        title_set = set(title_tokens)
        
        # Check for important keywords in title
        keyword_bonus = 0.0
        for term in query_terms:
            if term in ChineseConfig.KEYWORD_BOOSTS and term in title_set:
                keyword_bonus += ChineseConfig.KEYWORD_BOOSTS[term] * 2.0  # Extra bonus for keywords in title
        
        # Exact title match (all query terms in title)
        if query_set.issubset(title_set):
            return ChineseConfig.TITLE_EXACT_MATCH_BONUS + keyword_bonus
        
        # Partial title match
        intersection = query_set.intersection(title_set)
        if intersection:
            # Calculate match ratio
            match_ratio = len(intersection) / len(query_set)
            
            # Bonus based on match ratio
            if match_ratio >= 0.8:
                return ChineseConfig.TITLE_PARTIAL_MATCH_BONUS[0.8] + keyword_bonus
            elif match_ratio >= 0.6:
                return ChineseConfig.TITLE_PARTIAL_MATCH_BONUS[0.6] + keyword_bonus
            elif match_ratio >= 0.4:
                return ChineseConfig.TITLE_PARTIAL_MATCH_BONUS[0.4] + keyword_bonus
            else:
                return 2.0 + keyword_bonus
        
        # Check for substring matches in title
        title_text = doc_title.lower()
        query_text = ' '.join(query_terms).lower()
        
        if query_text in title_text:
            return ChineseConfig.TITLE_SUBSTRING_MATCH_BONUS + keyword_bonus
        
        return keyword_bonus
    
    def _calculate_bm25_score(self, query_terms: List[str], doc_id: int) -> float:
        """Calculate BM25 score for Chinese text with enhanced keyword weighting"""
        if doc_id not in self.document_index:
            return 0.0
        
        doc_data = self.document_index[doc_id]
        doc_length = doc_data['length']
        term_frequencies = doc_data['term_frequencies']
        doc_title = doc_data.get('title', '')
        
        score = 0.0
        
        # Count query term frequencies for better scoring
        query_term_counts = Counter(query_terms)
        
        for term, query_freq in query_term_counts.items():
            if term in term_frequencies:
                tf = term_frequencies[term]  # Term frequency in document
                idf = self._calculate_idf(term)
                
                # Get keyword boost multiplier
                keyword_boost = self._get_keyword_boost(term)
                
                # BM25 formula with query term frequency consideration and keyword boost
                numerator = tf * (self.k1 + 1)
                denominator = tf + self.k1 * (1 - self.b + self.b * (doc_length / self.avg_doc_length))
                
                term_score = idf * (numerator / denominator) * query_freq * keyword_boost
                score += term_score
        
        # Add enhanced title match bonus
        title_bonus = self._calculate_title_match_score(query_terms, doc_title)
        score += title_bonus
        
        return score
    
    def search(self, query: str, limit: int = None) -> List[Dict]:
        """
        Search Chinese documents using enhanced BM25 with keyword boosting
        """
        if limit is None:
            limit = ChineseConfig.DEFAULT_RESULTS_LIMIT
        limit = min(limit, ChineseConfig.MAX_RESULTS_LIMIT)
        
        # Process Chinese query
        query_terms = self.processor.preprocess_text(query)
        if not query_terms:
            return []
        
        print(f"🔍 Chinese search terms: {query_terms}")
        
        # Check for boosted keywords in query
        boosted_terms = [term for term in query_terms if term in ChineseConfig.KEYWORD_BOOSTS]
        if boosted_terms:
            print(f"🚀 Boosted keywords found: {boosted_terms}")
        
        # Find candidate documents
        candidate_docs = set()
        for term in query_terms:
            if term in self.inverted_index:
                for doc_id, _ in self.inverted_index[term]:
                    candidate_docs.add(doc_id)
        
        if not candidate_docs:
            print("❌ No documents found containing query terms")
            return []
        
        print(f"📄 Found {len(candidate_docs)} candidate documents")
        
        # Calculate enhanced BM25 scores with keyword boosting
        scored_docs = []
        for doc_id in candidate_docs:
            doc_data = self.document_index[doc_id]
            doc_title = doc_data.get('title', '')
            
            # Calculate base BM25 score with keyword boosting
            base_score = 0.0
            query_term_counts = Counter(query_terms)
            
            for term, query_freq in query_term_counts.items():
                if term in doc_data['term_frequencies']:
                    tf = doc_data['term_frequencies'][term]
                    idf = self._calculate_idf(term)
                    keyword_boost = self._get_keyword_boost(term)
                    
                    numerator = tf * (self.k1 + 1)
                    denominator = tf + self.k1 * (1 - self.b + self.b * (doc_data['length'] / self.avg_doc_length))
                    
                    term_score = idf * (numerator / denominator) * query_freq * keyword_boost
                    base_score += term_score
            
            # Calculate enhanced title match bonus
            title_bonus = self._calculate_title_match_score(query_terms, doc_title)
            total_score = base_score + title_bonus
            
            # Include documents that contain the query terms, even if score is 0
            if total_score >= 0:
                scored_docs.append({
                    'doc_id': doc_id,
                    'score': total_score,
                    'base_score': base_score,
                    'title_bonus': title_bonus,
                    'path': doc_data['path'],
                    'title': doc_title,
                    'length': doc_data['length'],
                    'chinese_chars': doc_data.get('chinese_chars', 0),
                    'relevance': 'high' if total_score > 8.0 else 'medium' if total_score > 3.0 else 'low'
                })
        
        # Sort by score descending
        scored_docs.sort(key=lambda x: x['score'], reverse=True)
        return scored_docs[:limit]
    
    def get_chinese_snippet(self, doc_path: str, query: str, snippet_length: int = 300) -> str:
        """
        Extract relevant Chinese text snippet containing query terms
        """
        try:
            from pathlib import Path
            import re
            
            # Handle path mapping - convert /app/documents/ to actual documents path
            if doc_path.startswith('/app/documents/'):
                filename = Path(doc_path).name
                actual_path = ChineseConfig.DOCUMENTS_DIR / filename
                
                # If exact filename doesn't exist, try to find similar files
                if not actual_path.exists():
                    # Try to find files with similar names using multiple strategies
                    import glob
                    filename_base = filename.replace('.txt', '').replace('.md', '')
                    
                    # Try different matching patterns
                    patterns = [
                        str(ChineseConfig.DOCUMENTS_DIR / f"*{filename_base}*"),
                        str(ChineseConfig.DOCUMENTS_DIR / f"*{filename_base.split('产品标准')[0]}*") if '产品标准' in filename_base else None,
                        str(ChineseConfig.DOCUMENTS_DIR / f"*{filename_base.split('SOP')[0]}*") if 'SOP' in filename_base else None,
                    ]
                    
                    matches = []
                    for pattern in patterns:
                        if pattern:
                            matches = glob.glob(pattern)
                            if matches:
                                break
                    
                    if matches:
                        actual_path = Path(matches[0])  # Use first match
                
                doc_path = str(actual_path)
            
            # Read file with Chinese encoding support
            content = self.processor._read_file_with_encoding(Path(doc_path))
            if not content:
                return "无法读取文件内容"
            
            query_terms = self.processor.preprocess_text(query)
            if not query_terms:
                return content[:snippet_length] + "..." if len(content) > snippet_length else content
            
            # Find best snippet containing most query terms
            sentences = re.split(r'[。！？\n]', content)
            best_sentence = ""
            best_score = 0
            
            for sentence in sentences:
                if len(sentence.strip()) < 10:
                    continue
                    
                sentence_terms = self.processor.preprocess_text(sentence)
                score = sum(1 for term in query_terms if term in sentence_terms)
                
                if score > best_score:
                    best_score = score
                    best_sentence = sentence.strip()
            
            # If no good sentence found, use beginning of document
            if not best_sentence:
                best_sentence = content[:snippet_length]
            
            # Truncate to length limit
            if len(best_sentence) > snippet_length:
                best_sentence = best_sentence[:snippet_length] + "..."
            
            return best_sentence
            
        except Exception as e:
            return f"读取片段时出错: {e}"
    
    def get_term_statistics(self, term: str) -> Dict:
        """Get statistics for a Chinese term"""
        processed_terms = self.processor.preprocess_text(term)
        if not processed_terms:
            return {'error': '无法处理查询词'}
        
        term = processed_terms[0]
        
        if term not in self.inverted_index:
            return {
                'term': term,
                'document_frequency': 0,
                'total_frequency': 0,
                'message': '词汇不在索引中'
            }
        
        doc_freq = len(self.inverted_index[term])
        total_freq = sum(freq for _, freq in self.inverted_index[term])
        idf = self._calculate_idf(term)
        
        return {
            'term': term,
            'document_frequency': doc_freq,
            'total_frequency': total_freq,
            'idf_score': round(idf, 4),
            'coverage': f"{doc_freq}/{self.num_documents} documents",
            'documents': self.inverted_index[term][:5]  # Show first 5 documents
        }
    
    def get_similar_documents(self, doc_id: int, limit: int = 5) -> List[Dict]:
        """Find similar Chinese documents using term overlap"""
        if doc_id not in self.document_index:
            return []
        
        source_terms = set(self.document_index[doc_id]['term_frequencies'].keys())
        
        similarities = []
        for other_doc_id, other_doc_data in self.document_index.items():
            if other_doc_id == doc_id:
                continue
            
            other_terms = set(other_doc_data['term_frequencies'].keys())
            
            # Calculate Jaccard similarity
            intersection = len(source_terms.intersection(other_terms))
            union = len(source_terms.union(other_terms))
            
            if union > 0:
                similarity = intersection / union
                similarities.append({
                    'doc_id': other_doc_id,
                    'similarity_score': round(similarity, 4),
                    'path': other_doc_data['path'],
                    'title': other_doc_data['title'],
                    'shared_terms': intersection,
                    'total_terms': len(other_terms)
                })
        
        similarities.sort(key=lambda x: x['similarity_score'], reverse=True)
        return similarities[:limit]
    
    def analyze_query(self, query: str) -> Dict:
        """Analyze Chinese query and provide insights"""
        query_terms = self.processor.preprocess_text(query)
        
        analysis = {
            'original_query': query,
            'processed_terms': query_terms,
            'term_count': len(query_terms),
            'term_analysis': []
        }
        
        for term in query_terms:
            term_stats = self.get_term_statistics(term)
            analysis['term_analysis'].append({
                'term': term,
                'frequency': term_stats.get('total_frequency', 0),
                'document_coverage': term_stats.get('document_frequency', 0),
                'rarity_score': 'rare' if term_stats.get('document_frequency', 0) < 2 else 'common'
            })
        
        return analysis
