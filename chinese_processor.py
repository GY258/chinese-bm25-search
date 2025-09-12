import os
import re
import json
import pickle
import logging
from pathlib import Path
from collections import defaultdict, Counter
from typing import List, Dict, Tuple, Set
import jieba
import jieba.posseg as pseg
from config import ChineseConfig

# Configure jieba logging
jieba.setLogLevel(logging.INFO)

class ChineseDocumentProcessor:
    """
    High-performance Chinese document processor inspired by Elasticsearch's SmartCN
    Uses jieba segmentation with HMM for optimal Chinese text processing
    """
    
    def __init__(self):
        self.stop_words = set()
        self.custom_dict_loaded = False
        self._initialize_chinese_processing()
        
    def _initialize_chinese_processing(self):
        """Initialize Chinese text processing with optimized settings"""
        
        # Chinese stop words (based on common usage patterns)
        self.stop_words = {
            # Function words and particles
            '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '这个', '那个',
            '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这', '那',
            '里', '个', '们', '能', '对', '时', '下', '大', '来', '为', '多', '么', '什', '又', '可', '还',
            '只', '从', '用', '他', '她', '它', '我们', '你们', '他们', '她们', '它们', '这些', '那些',
            '什么', '怎么', '为什么', '因为', '所以', '但是', '然后', '如果', '虽然', '而且', '或者',
            # Numbers and quantifiers that might not be useful for search
            '第一', '第二', '第三', '几个', '一些', '很多', '一点', '有些',
            # Common punctuation that might slip through
            '，', '。', '！', '？', ';', '：', '"', '"', ''', ''', '（', '）', '【', '】', '《', '》',
            '、', '　', '…', '—', '–', '·', '〈', '〉', '「', '」', '『', '』', '［', '］', '｛', '｝'
        }
        
        # Enable parallel processing for jieba (4 threads for better performance)
        jieba.enable_parallel(4)
        
        # Initialize with precise mode (better for search applications)
        jieba.initialize()
        
        print(f"🇨🇳 Chinese processor initialized")
        print(f"   Stop words: {len(self.stop_words)}")
        print(f"   Processing mode: Precise segmentation with HMM")
        print(f"   Title extraction: Enabled with 5x boosted indexing")
        
    def add_custom_dictionary(self, documents_sample: List[Path] = None):
        """
        Build and load custom dictionary from document collection
        This improves segmentation accuracy for domain-specific terms
        """
        if self.custom_dict_loaded:
            return
            
        print("📚 Building custom dictionary from documents...")
        
        # If no sample provided, use first few documents from config directory
        if not documents_sample:
            documents_sample = list(ChineseConfig.DOCUMENTS_DIR.glob('*.txt'))[:5]
        
        term_counts = Counter()
        
        for doc_path in documents_sample:
            try:
                text = self._read_file_with_encoding(doc_path)
                if text and len(text) > 100:  # Only process substantial documents
                    # Extract potential terms using basic segmentation
                    words = jieba.cut(text, cut_all=False)
                    for word in words:
                        word = word.strip()
                        if (len(word) >= 2 and 
                            re.search(r'[\u4e00-\u9fff]', word) and  # Contains Chinese
                            word not in self.stop_words):
                            term_counts[word] += 1
            except Exception as e:
                print(f"   Warning: Could not process {doc_path}: {e}")
                continue
        
        # Create custom dictionary file
        custom_dict_path = ChineseConfig.INDEX_DIR / 'custom_dict.txt'
        ChineseConfig.create_directories()
        
        with open(custom_dict_path, 'w', encoding='utf-8') as f:
            # Add terms that appear at least twice
            added_terms = 0
            for term, count in term_counts.most_common():
                if count >= 2 and len(term) >= 2:
                    f.write(f"{term} {count} n\n")  # n = noun (default POS)
                    added_terms += 1
                    if added_terms >= 1000:  # Limit dictionary size
                        break
        
        if added_terms > 0:
            # Load the custom dictionary
            jieba.load_userdict(str(custom_dict_path))
            self.custom_dict_loaded = True
            print(f"   ✅ Custom dictionary created with {added_terms} terms")
        else:
            print("   ⚠️  No custom terms found, using default dictionary")
    
    def _read_file_with_encoding(self, file_path: Path) -> str:
        """Read file with Chinese encoding detection"""
        encodings = ['utf-8', 'gbk', 'gb2312', 'big5']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
                    content = f.read()
                    # Prefer encoding that gives us Chinese characters
                    if re.search(r'[\u4e00-\u9fff]', content):
                        return content
                    elif encoding == 'utf-8':  # Fallback
                        return content
            except (UnicodeDecodeError, FileNotFoundError):
                continue
        
        return ""
    
    def extract_title_from_content(self, text_content: str, filename: str) -> str:
        """
        Extract title from document content using multiple strategies
        Returns the best title found or falls back to filename
        """
        if not text_content or not text_content.strip():
            return filename
        
        # Strategy 1: Look for markdown-style headers (# Title)
        markdown_headers = re.findall(r'^#+\s*(.+)$', text_content, re.MULTILINE)
        if markdown_headers:
            # Take the first header that's not too long
            for header in markdown_headers:
                header = header.strip()
                if 3 <= len(header) <= 50 and re.search(r'[\u4e00-\u9fff]', header):
                    return header
        
        # Strategy 2: Look for Chinese title patterns
        # Common patterns: "标题：", "题目：", "主题：", etc.
        title_patterns = [
            r'标题[：:]\s*(.+)',
            r'题目[：:]\s*(.+)',
            r'主题[：:]\s*(.+)',
            r'名称[：:]\s*(.+)',
            r'^(.+?)[：:]\s*$',  # General pattern: "Title:"
        ]
        
        for pattern in title_patterns:
            matches = re.findall(pattern, text_content, re.MULTILINE)
            for match in matches:
                match = match.strip()
                if (3 <= len(match) <= 50 and 
                    re.search(r'[\u4e00-\u9fff]', match) and
                    not re.search(r'[。！？]', match)):  # Not a sentence
                    return match
        
        # Strategy 3: Extract from first meaningful line
        lines = text_content.split('\n')
        for line in lines[:10]:  # Check first 10 lines
            line = line.strip()
            if (len(line) >= 3 and len(line) <= 50 and
                re.search(r'[\u4e00-\u9fff]', line) and
                not re.search(r'[。！？]', line) and  # Not a sentence
                not re.search(r'^\d+[、.]', line)):  # Not numbered list
                return line
        
        # Strategy 4: Extract meaningful part from filename
        # Remove extension and common prefixes/suffixes
        clean_filename = filename
        if '.' in clean_filename:
            clean_filename = clean_filename.rsplit('.', 1)[0]
        
        # Remove common date patterns
        clean_filename = re.sub(r'\d{8,}', '', clean_filename)  # Remove dates like 20241228
        clean_filename = re.sub(r'[_-]', ' ', clean_filename)  # Replace separators with spaces
        clean_filename = clean_filename.strip()
        
        if clean_filename and len(clean_filename) >= 3:
            return clean_filename
        
        return filename
    
    def preprocess_text(self, text: str) -> List[str]:
        """
        Advanced Chinese text preprocessing using jieba segmentation
        Implements SmartCN-inspired processing pipeline
        """
        if not text or not text.strip():
            return []
        
        # Clean and normalize text
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove non-Chinese characters except letters and numbers (optional)
        # Keep Chinese characters, English letters, and numbers
        text = re.sub(r'[^\u4e00-\u9fff\w\s]', ' ', text)
        
        if ChineseConfig.ENABLE_POS_FILTERING:
            # Use part-of-speech tagging for better precision
            words = pseg.cut(text)
            
            # Keep meaningful parts of speech (similar to SmartCN filtering)
            meaningful_pos = {
                'n',   # noun
                'nr',  # person name
                'ns',  # place name
                'nt',  # organization name
                'nz',  # other proper noun
                'v',   # verb
                'vd',  # adverbial verb
                'vn',  # verb-noun
                'a',   # adjective
                'ad',  # adverbial adjective
                'an',  # adjective-noun
                'i',   # idiom
                'l',   # temporary idiom
                'j',   # abbreviation
                'eng', # English words
                'm',   # measure word (e.g., 克, 个, 杯)
                'x',   # unknown words (often domain-specific terms)
            }
            
            tokens = []
            for word, pos in words:
                word = word.strip()
                if (pos in meaningful_pos and
                    len(word) >= ChineseConfig.MIN_TERM_LENGTH and
                    word not in self.stop_words):
                    tokens.append(word)
        else:
            # Fast segmentation without POS tagging
            words = jieba.cut(text, cut_all=False, HMM=True)  # Enable HMM
            tokens = [word.strip() for word in words 
                     if (len(word.strip()) >= ChineseConfig.MIN_TERM_LENGTH and 
                         word.strip() not in self.stop_words)]
        
        return tokens
    
    def find_documents(self, root_dir: Path) -> List[Path]:
        """Find all supported Chinese documents"""
        documents = []
        
        print(f"🔍 Scanning for documents in: {root_dir}")
        
        for ext in ChineseConfig.SUPPORTED_EXTENSIONS:
            pattern = f"**/*{ext}"
            found_files = list(root_dir.glob(pattern))
            documents.extend(found_files)
            print(f"   Found {len(found_files)} {ext} files")
        
        # Filter valid documents
        valid_documents = []
        for doc in documents:
            try:
                if (doc.is_file() and 
                    0 < doc.stat().st_size <= ChineseConfig.MAX_DOC_SIZE):
                    valid_documents.append(doc)
            except Exception:
                continue
        
        print(f"✅ Total valid documents: {len(valid_documents)}")
        return valid_documents
    
    def process_documents(self, documents: List[Path]) -> Tuple[Dict[int, Dict], Dict[str, List[Tuple[int, int]]]]:
        """Process Chinese documents with optimized segmentation and title indexing with 5x weight"""
        
        # Build custom dictionary first
        if not self.custom_dict_loaded:
            self.add_custom_dictionary(documents[:3])  # Use first 3 docs for dictionary
        
        document_index = {}
        inverted_index = defaultdict(list)
        
        print(f"🔄 Processing {len(documents)} Chinese documents with title extraction...")
        
        stats = {
            'total_chars': 0,
            'total_tokens': 0,
            'chinese_docs': 0,
            'processed_docs': 0,
            'titles_extracted': 0
        }
        
        for doc_id, doc_path in enumerate(documents):
            if doc_id % 10 == 0:
                print(f"   📄 Progress: {doc_id}/{len(documents)} documents")
                
            # Read document content
            text_content = self._read_file_with_encoding(doc_path)
            if not text_content.strip():
                continue
            
            # Check for Chinese content
            chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text_content))
            if chinese_chars < 5:  # Skip if insufficient Chinese content
                continue
            
            stats['chinese_docs'] += 1
            stats['total_chars'] += len(text_content)
            
            # Extract title from content
            extracted_title = self.extract_title_from_content(text_content, doc_path.name)
            if extracted_title != doc_path.name:
                stats['titles_extracted'] += 1
            
            # Process document content with Chinese segmentation
            content_tokens = self.preprocess_text(text_content)
            if not content_tokens:
                continue
            
            # Process title with Chinese segmentation
            title_tokens = self.preprocess_text(extracted_title)
            
            # Combine content and title tokens with boosted title weights
            # Title terms get 5x weight to make them more searchable
            combined_tokens = content_tokens.copy()
            for title_token in title_tokens:
                # Add title token 5 times to boost its weight
                combined_tokens.extend([title_token] * 5)
            
            stats['total_tokens'] += len(combined_tokens)
            stats['processed_docs'] += 1
            
            # Calculate term frequencies (title terms will have higher frequency)
            term_frequencies = Counter(combined_tokens)
            
            # Store document metadata with both filename and extracted title
            document_index[doc_id] = {
                'path': str(doc_path),
                'title': extracted_title,  # Use extracted title instead of filename
                'filename': doc_path.name,  # Keep original filename
                'tokens': len(content_tokens),  # Content tokens only
                'title_tokens': len(title_tokens),  # Title tokens
                'length': len(combined_tokens),  # Combined length for BM25
                'term_frequencies': term_frequencies,
                'chinese_chars': chinese_chars,
                'total_chars': len(text_content)
            }
            
            # Update inverted index with boosted title terms
            for term, freq in term_frequencies.items():
                inverted_index[term].append((doc_id, freq))
        
        # Print processing statistics
        print(f"\n📊 Processing Results:")
        print(f"   Successfully processed: {stats['processed_docs']} documents")
        print(f"   Chinese documents: {stats['chinese_docs']}")
        print(f"   Titles extracted: {stats['titles_extracted']}")
        print(f"   Total characters: {stats['total_chars']:,}")
        print(f"   Total tokens extracted: {stats['total_tokens']:,}")
        print(f"   Unique terms (vocabulary): {len(inverted_index):,}")
        if stats['processed_docs'] > 0:
            print(f"   Average tokens per document: {stats['total_tokens']/stats['processed_docs']:.1f}")
            print(f"   Title extraction rate: {stats['titles_extracted']/stats['processed_docs']*100:.1f}%")
        
        return document_index, dict(inverted_index)
    
    def save_index(self, document_index: Dict, inverted_index: Dict, index_dir: Path):
        """Save Chinese index with metadata including extracted titles"""
        index_dir.mkdir(exist_ok=True)
        
        # Save document index
        with open(index_dir / 'chinese_documents.json', 'w', encoding='utf-8') as f:
            serializable_docs = {}
            for doc_id, doc_data in document_index.items():
                serializable_docs[doc_id] = {
                    'path': doc_data['path'],
                    'title': doc_data['title'],
                    'filename': doc_data.get('filename', doc_data['title']),
                    'tokens': doc_data['tokens'],
                    'title_tokens': doc_data.get('title_tokens', 0),
                    'length': doc_data['length'],
                    'term_frequencies': dict(doc_data['term_frequencies']),
                    'chinese_chars': doc_data.get('chinese_chars', 0),
                    'total_chars': doc_data.get('total_chars', 0)
                }
            json.dump(serializable_docs, f, indent=2, ensure_ascii=False)
        
        # Save inverted index
        with open(index_dir / 'chinese_inverted_index.pkl', 'wb') as f:
            pickle.dump(inverted_index, f)
        
        print(f"💾 Chinese index with searchable titles (5x weight) saved to {index_dir}")
    
    def load_index(self, index_dir: Path) -> Tuple[Dict, Dict]:
        """Load Chinese index from disk"""
        with open(index_dir / 'chinese_documents.json', 'r', encoding='utf-8') as f:
            document_index = json.load(f)
            
        # Convert and restore data structures
        processed_docs = {}
        for doc_id, doc_data in document_index.items():
            processed_docs[int(doc_id)] = {
                'path': doc_data['path'],
                'title': doc_data['title'],
                'filename': doc_data.get('filename', doc_data['title']),
                'tokens': doc_data['tokens'],
                'title_tokens': doc_data.get('title_tokens', 0),
                'length': doc_data['length'],
                'term_frequencies': Counter(doc_data['term_frequencies']),
                'chinese_chars': doc_data.get('chinese_chars', 0),
                'total_chars': doc_data.get('total_chars', 0)
            }
        
        with open(index_dir / 'chinese_inverted_index.pkl', 'rb') as f:
            inverted_index = pickle.load(f)
            
        return processed_docs, inverted_index
