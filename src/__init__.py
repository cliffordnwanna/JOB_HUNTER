# JOB_HUNTER src package - Production Grade v2.0
# Dynamic LLM-based extraction with PII sanitization

# Main components (import directly from v2 modules)
from .parser_v2 import EnhancedCVParser, DynamicCVParser
from .scraper import JobScraper
from .matcher_v2 import JobMatcher, DynamicJobMatcher, DynamicTFIDFMatcher, BertSemanticMatcher, AzureSemanticMatcher
from .ui import load_css, show_loading_screen, display_job_card

# Internal modules (for advanced use)
from .pii_sanitizer import PIISanitizer, PrivacyPreservingExtractor
from .llm_extractor import HybridExtractor, CVExtractionResult
from .model_manager import ModelManager, warmup_on_startup, model_manager

__all__ = [
    # Main API
    'EnhancedCVParser',
    'DynamicCVParser',
    'JobScraper', 
    'JobMatcher',
    'DynamicJobMatcher',
    
    # Privacy & Extraction
    'PIISanitizer',
    'PrivacyPreservingExtractor',
    'HybridExtractor',
    'CVExtractionResult',
    
    # Matching engines
    'DynamicTFIDFMatcher',
    'BertSemanticMatcher',
    'AzureSemanticMatcher',
    
    # Model management
    'ModelManager',
    'warmup_on_startup',
    'model_manager',
    
    # UI
    'load_css',
    'show_loading_screen',
    'display_job_card'
]
