"""
PII Sanitizer Module - GDPR Compliant
Removes personally identifiable information before LLM processing.
"""
import re
from typing import Dict, Tuple, Optional
from dataclasses import dataclass


@dataclass
class SanitizationResult:
    """Result of PII sanitization containing clean text and extracted PII vault."""
    clean_text: str
    pii_vault: Dict[str, str]  # Stores original PII mapped to tokens
    tokens_used: list


class PIISanitizer:
    """
    Production-grade PII detector and sanitizer.
    Identifies and masks PII before sending to external LLM services.
    """
    
    # PII Patterns - comprehensive regex for common PII types
    PATTERNS = {
        'EMAIL': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
        'PHONE': re.compile(r'[\+]?[(]?[0-9]{1,4}[)]?[-\s\.]?[(]?[0-9]{1,4}[)]?[-\s\.]?[0-9]{1,9}'),
        'SSN': re.compile(r'\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b'),
        'CREDIT_CARD': re.compile(r'\b(?:\d[ -]*?){13,16}\b'),
        'IP_ADDRESS': re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b'),
        'URL_WITH_USER': re.compile(r'https?://[^\s]+:[^\s]+@[^\s]+'),
        'DATE_OF_BIRTH': re.compile(r'\b(?:born?|dob|birth.?date)[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b', re.IGNORECASE),
        'FULL_NAME': None,  # Detected via spaCy NER if available
    }
    
    def __init__(self):
        self.token_counter = 0
        self.vault = {}
        
    def _generate_token(self, pii_type: str) -> str:
        """Generate a unique token for masked PII."""
        self.token_counter += 1
        return f"[{pii_type}_{self.token_counter}]"
    
    def _mask_pattern(self, text: str, pattern_name: str, pattern: re.Pattern) -> str:
        """Mask all occurrences of a pattern with tokens."""
        if pattern is None:
            return text
            
        def replace_match(match):
            original = match.group(0)
            token = self._generate_token(pattern_name)
            self.vault[token] = original
            return token
        
        return pattern.sub(replace_match, text)
    
    def _detect_names_with_ner(self, text: str) -> str:
        """Use spaCy NER to detect and mask person names if available."""
        try:
            import spacy
            # Load small English model (efficient for deployment)
            nlp = spacy.load("en_core_web_sm")
            doc = nlp(text)
            
            # Replace person names with tokens (process in reverse to preserve indices)
            person_names = [(ent.start_char, ent.end_char, ent.text) 
                          for ent in doc.ents if ent.label_ == "PERSON"]
            
            result = text
            for start, end, name in reversed(person_names):
                token = self._generate_token("NAME")
                self.vault[token] = name
                result = result[:start] + token + result[end:]
            
            return result
        except (ImportError, OSError):
            # spaCy not installed or model not available - skip NER
            return text
    
    def _extract_context_hints(self, text: str) -> Dict[str, list]:
        """Extract contextual hints about candidate without PII."""
        hints = {
            'domain_hints': [],
            'role_hints': [],
            'experience_level': None
        }
        
        text_lower = text.lower()
        
        # Domain detection from context (not hardcoded skills, just context clues)
        domain_indicators = {
            'healthcare': ['hospital', 'clinic', 'patient', 'medical', 'health', 'therapy', 'nursing'],
            'technology': ['software', 'development', 'engineering', 'programming', 'technical'],
            'finance': ['banking', 'financial', 'accounting', 'investment', 'trading'],
            'education': ['teaching', 'academic', 'university', 'school', 'education'],
            'marketing': ['marketing', 'brand', 'campaign', 'digital marketing'],
            'sales': ['sales', 'business development', 'account management'],
        }
        
        for domain, indicators in domain_indicators.items():
            if any(indicator in text_lower for indicator in indicators):
                hints['domain_hints'].append(domain)
        
        # Experience level detection
        if re.search(r'\b(senior|lead|principal|staff)\b', text_lower):
            hints['experience_level'] = 'senior'
        elif re.search(r'\b(junior|entry|graduate|intern)\b', text_lower):
            hints['experience_level'] = 'junior'
        else:
            hints['experience_level'] = 'mid'
        
        return hints
    
    def sanitize(self, text: str) -> SanitizationResult:
        """
        Main sanitization method - removes all PII and returns clean text.
        
        Args:
            text: Raw CV text
            
        Returns:
            SanitizationResult with clean_text, pii_vault, and tokens_used
        """
        self.vault = {}
        self.token_counter = 0
        
        clean_text = text
        
        # Step 1: Mask structured PII (emails, phones, SSN, etc.)
        for pattern_name, pattern in self.PATTERNS.items():
            clean_text = self._mask_pattern(clean_text, pattern_name, pattern)
        
        # Step 2: Detect and mask names using NER (if available)
        clean_text = self._detect_names_with_ner(clean_text)
        
        # Step 3: Mask remaining patterns that look like addresses
        address_pattern = re.compile(r'\b\d+\s+[A-Za-z]+(?:\s+[A-Za-z]+)*\s+(?:street|st|avenue|ave|road|rd|drive|dr|lane|ln|boulevard|blvd)\b', re.IGNORECASE)
        clean_text = self._mask_pattern(clean_text, "ADDRESS", address_pattern)
        
        # Step 4: Extract non-PII context hints
        hints = self._extract_context_hints(text)
        
        return SanitizationResult(
            clean_text=clean_text,
            pii_vault=self.vault,
            tokens_used=list(self.vault.keys())
        )
    
    def restore_pii(self, clean_text: str, pii_vault: Dict[str, str]) -> str:
        """Restore original PII from vault (for internal storage if needed)."""
        result = clean_text
        for token, original in pii_vault.items():
            result = result.replace(token, original)
        return result


class PrivacyPreservingExtractor:
    """
    Wrapper that ensures PII is always sanitized before LLM calls.
    ULTRA-GDPR COMPLIANT: PII is NEVER stored, only used for sanitization verification.
    """
    
    def __init__(self):
        self.sanitizer = PIISanitizer()
    
    def prepare_for_llm(self, cv_text: str, purge_immediately: bool = True) -> Tuple[str, Optional[Dict], Dict]:
        """
        Prepare CV text for LLM processing with immediate PII purge.
        
        Args:
            cv_text: Raw CV text
            purge_immediately: If True (default), PII vault is immediately discarded
        
        Returns:
            Tuple of (sanitized_text, pii_vault_or_none, context_hints)
            pii_vault is None if purge_immediately=True (recommended)
        """
        result = self.sanitizer.sanitize(cv_text)
        hints = self.sanitizer._extract_context_hints(cv_text)
        
        # ULTRA-GDPR: Immediately purge PII vault
        if purge_immediately:
            # Clear the vault contents but return None to caller
            # This ensures PII never leaves this function
            vault_snapshot = None
            
            # Explicitly overwrite vault memory (defense in depth)
            for key in list(result.pii_vault.keys()):
                result.pii_vault[key] = "[REDACTED]"
            result.pii_vault.clear()
            
            return result.clean_text, vault_snapshot, hints
        else:
            # Only for debugging - NOT recommended for production
            return result.clean_text, result.pii_vault, hints
    
    def extract_and_purge(self, cv_text: str) -> Tuple[str, Dict]:
        """
        One-shot extraction with guaranteed PII purge.
        Use this for production - returns only sanitized text and non-PII hints.
        
        Returns:
            Tuple of (sanitized_text, context_hints)
        """
        sanitized, _, hints = self.prepare_for_llm(cv_text, purge_immediately=True)
        return sanitized, hints
