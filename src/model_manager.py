"""
Optimized Model Manager for Fast Loading
Caches models in memory and provides warmup functionality.
"""
import os
import streamlit as st
from typing import Optional, Dict, Any


class ModelManager:
    """
    Singleton model manager for efficient model loading.
    Uses Streamlit cache_resource for persistence across sessions.
    """
    
    _instance = None
    _models: Dict[str, Any] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelManager, cls).__new__(cls)
        return cls._instance
    
    @staticmethod
    @st.cache_resource(show_spinner=False)
    def _load_bert_model(model_name: str = "all-MiniLM-L6-v2"):
        """
        Load and cache BERT model using Streamlit's cache_resource.
        This persists across reruns and is shared between users.
        """
        try:
            from sentence_transformers import SentenceTransformer
            print(f"🔄 Loading BERT model: {model_name}")
            model = SentenceTransformer(model_name)
            print(f"✅ BERT model loaded successfully")
            return model
        except Exception as e:
            print(f"❌ Failed to load BERT model: {e}")
            return None
    
    @staticmethod
    @st.cache_resource(show_spinner=False)
    def _load_spacy_model(model_name: str = "en_core_web_sm"):
        """
        Load and cache spaCy model.
        """
        try:
            import spacy
            print(f"🔄 Loading spaCy model: {model_name}")
            nlp = spacy.load(model_name)
            print(f"✅ spaCy model loaded successfully")
            return nlp
        except Exception as e:
            print(f"❌ Failed to load spaCy model: {e}")
            return None
    
    def get_bert_model(self, model_name: str = "all-MiniLM-L6-v2") -> Optional[Any]:
        """Get cached BERT model or load it."""
        cache_key = f"bert_{model_name}"
        
        if cache_key not in self._models or self._models[cache_key] is None:
            self._models[cache_key] = self._load_bert_model(model_name)
        
        return self._models[cache_key]
    
    def get_spacy_model(self, model_name: str = "en_core_web_sm") -> Optional[Any]:
        """Get cached spaCy model or load it."""
        cache_key = f"spacy_{model_name}"
        
        if cache_key not in self._models or self._models[cache_key] is None:
            self._models[cache_key] = self._load_spacy_model(model_name)
        
        return self._models[cache_key]
    
    def warmup_models(self, models: list = None):
        """
        Pre-load models on app startup to ensure fast first-use.
        Call this in app.py on startup.
        
        Args:
            models: List of model names to warmup ['bert', 'spacy'] or None for all
        """
        if models is None:
            models = ['bert', 'spacy']
        
        for model in models:
            if model == 'bert':
                self.get_bert_model()
            elif model == 'spacy':
                self.get_spacy_model()
    
    def clear_cache(self):
        """Clear all cached models (useful for memory management)."""
        self._models.clear()
        # Note: Streamlit cache_resource clears on app restart only


# Global instance
model_manager = ModelManager()


def warmup_on_startup(models: list = None):
    """
    Call this in app.py to pre-load models.
    Example:
        from src.model_manager import warmup_on_startup
        warmup_on_startup(['bert'])  # Pre-load BERT only for speed
    """
    manager = ModelManager()
    manager.warmup_models(models)
    return manager
