# DEPRECATED: Use matcher_v2 directly
# This file is kept for backward compatibility but will be removed in v3.0
# Import from matcher_v2 instead: from src.matcher_v2 import JobMatcher
from .matcher_v2 import (
    DynamicJobMatcher, 
    DynamicTFIDFMatcher, 
    BertSemanticMatcher, 
    AzureSemanticMatcher,
    BaseMatcher,
    JobMatcher
)

__all__ = [
    'DynamicJobMatcher',
    'DynamicTFIDFMatcher', 
    'BertSemanticMatcher',
    'AzureSemanticMatcher',
    'BaseMatcher',
    'JobMatcher'
]
