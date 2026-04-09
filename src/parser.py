# DEPRECATED: Use parser_v2 directly
# This file is kept for backward compatibility but will be removed in v3.0
# Import from parser_v2 instead: from src.parser_v2 import EnhancedCVParser
from .parser_v2 import DynamicCVParser, EnhancedCVParser

__all__ = ['DynamicCVParser', 'EnhancedCVParser']
