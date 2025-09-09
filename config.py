import os
from pathlib import Path

class ChineseConfig:
    # BM25 parameters - optimized for Chinese text
    K1 = 1.5  # Slightly higher for Chinese (terms repeat less frequently)
    B = 0.6   # Lower B for Chinese (less length normalization needed)
    
    # Chinese document processing
    MAX_DOC_SIZE = 10 * 1024 * 1024  # 10MB max file size
    SUPPORTED_EXTENSIONS = ['.txt', '.md', '.doc', '.docx']
    
    # Index storage - 支持环境变量覆盖
    INDEX_DIR = Path(os.getenv('INDEX_DIR', str(Path(__file__).parent / 'chinese_index')))
    DOCUMENTS_DIR = Path(os.getenv('DOCUMENTS_DIR', str(Path(__file__).parent / 'documents')))
    
    # API configuration - 支持环境变量覆盖
    API_HOST = os.getenv('API_HOST', '0.0.0.0')
    API_PORT = int(os.getenv('API_PORT', '5002'))
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    
    # Search settings
    DEFAULT_RESULTS_LIMIT = 10
    MAX_RESULTS_LIMIT = 50
    
    # Chinese-specific settings
    USE_TRADITIONAL_CHINESE = False  # Set to True if you have traditional Chinese
    MIN_TERM_LENGTH = 1  # Chinese terms can be single characters
    ENABLE_POS_FILTERING = True  # Filter by part-of-speech tags
    
    @classmethod
    def create_directories(cls):
        """Create necessary directories if they don't exist"""
        cls.INDEX_DIR.mkdir(exist_ok=True)