"""
Dynamic Job Matcher v2.0
Uses semantic similarity for matching - no hardcoded skill synonyms.
"""
import os
import re
from typing import Dict, List, Set, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


class BaseMatcher:
    """Base class for matching logic."""
    
    def match(self, cv_data: Dict, job: Dict) -> float:
        raise NotImplementedError


class DynamicTFIDFMatcher(BaseMatcher):
    """
    Dynamic TF-IDF matcher that works with any domain.
    No hardcoded skill synonyms - uses semantic text similarity.
    """
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            stop_words="english",
            max_features=5000,  # Increased for better coverage
            ngram_range=(1, 3),  # Include trigrams for phrases
            min_df=1,  # Allow rare terms
            max_df=0.95  # Ignore overly common terms
        )
    
    def _build_cv_text(self, cv_data: Dict) -> str:
        """Build representative CV text from dynamic extraction."""
        parts = []
        
        # Professional title (weighted heavily)
        title = cv_data.get('professional_title', '')
        if title:
            parts.extend([title] * 3)  # Repeat for weight
        
        # Domain and industry
        domain = cv_data.get('domain', '')
        industry = cv_data.get('industry', '')
        if domain:
            parts.extend([domain] * 2)
        if industry:
            parts.append(industry)
        
        # Skills (all categories)
        skills = cv_data.get('skills', [])
        parts.extend(skills)
        
        # Raw skills text for context
        raw_skills = cv_data.get('raw_skills_text', '')
        if raw_skills:
            parts.append(raw_skills)
        
        # Job preferences
        preferences = cv_data.get('job_preferences', [])
        parts.extend(preferences)
        
        # Full text (truncated)
        full_text = cv_data.get('full_text', '')[:5000]
        if full_text:
            parts.append(full_text)
        
        return " ".join(parts).lower()
    
    def _build_job_text(self, job: Dict) -> str:
        """Build representative job text."""
        title = job.get('title', '')
        description = job.get('description', '')[:3000]
        tags = job.get('tags', [])
        
        parts = []
        # Title weighted heavily
        if title:
            parts.extend([title] * 3)
        
        # Tags (ensure all are strings)
        if isinstance(tags, list):
            parts.extend([str(tag) for tag in tags])
        elif tags:
            parts.append(str(tags))
        
        # Description
        if description:
            parts.append(str(description))
        
        # Ensure ALL parts are strings before join
        parts = [str(p) if p is not None else '' for p in parts]
        return " ".join(parts).lower()
    
    def match(self, cv_data: Dict, job: Dict) -> float:
        """
        Calculate match score using TF-IDF cosine similarity.
        Handles sparse CVs (very short) with fallback to keyword matching.
        """
        cv_text = self._build_cv_text(cv_data)
        job_text = self._build_job_text(job)
        
        if not cv_text or not job_text:
            return 0.0
        
        # Check for very short CV (sparse corpus issue)
        skills = cv_data.get('skills', [])
        is_short_cv = len(skills) < 3 and len(cv_text) < 500
        
        try:
            if is_short_cv:
                # Fallback: Simple keyword matching for short CVs
                return self._keyword_match(skills, cv_text, job_text)
            
            # TF-IDF vectors
            vectors = self.vectorizer.fit_transform([cv_text, job_text])
            
            # Cosine similarity
            similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
            
            # Convert to percentage
            score = float(similarity) * 100
            
            # Boost score based on explicit skill matches
            job_text_lower = job_text
            
            explicit_matches = sum(1 for skill in skills if skill.lower() in job_text_lower)
            if len(skills) > 0:
                match_ratio = explicit_matches / len(skills)
                # Blend TF-IDF with explicit match ratio
                score = (score * 0.7) + (match_ratio * 100 * 0.3)
            
            return round(min(score, 100), 2)
            
        except Exception as e:
            print(f"TF-IDF matching error: {e}")
            # Fallback to keyword matching on error
            return self._keyword_match(skills, cv_text, job_text)
    
    def _keyword_match(self, skills: List[str], cv_text: str, job_text: str) -> float:
        """
        Simple keyword-based matching fallback for short CVs.
        """
        if not skills:
            return 0.0
        
        job_text_lower = job_text.lower()
        cv_text_lower = cv_text.lower()
        
        # Count skill matches in job
        skill_matches = sum(1 for skill in skills if skill.lower() in job_text_lower)
        
        # Count general CV text overlap
        cv_words = set(cv_text_lower.split())
        job_words = set(job_text_lower.split())
        if cv_words and job_words:
            word_overlap = len(cv_words & job_words) / len(cv_words)
        else:
            word_overlap = 0.0
        
        # Combine scores
        skill_score = (skill_matches / len(skills)) * 100 if skills else 0.0
        combined = (skill_score * 0.7) + (word_overlap * 100 * 0.3)
        
        return round(min(combined, 100), 2)


class BertSemanticMatcher(BaseMatcher):
    """
    BERT-based semantic matcher using sentence-transformers.
    Uses cached models for speed via ModelManager.
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None
        self._load_model_cached()
    
    def _load_model_cached(self):
        """Load model from cache or initialize."""
        try:
            from .model_manager import model_manager
            self.model = model_manager.get_bert_model(self.model_name)
        except Exception as e:
            # Fallback to direct loading
            try:
                from sentence_transformers import SentenceTransformer
                self.model = SentenceTransformer(self.model_name)
                print(f"✅ BERT model loaded (direct): {self.model_name}")
            except Exception as e2:
                print(f"⚠️ BERT unavailable: {e2}")
    
    def _build_profile_text(self, cv_data: Dict) -> str:
        """Build professional profile description."""
        parts = []
        
        # Title and domain
        title = cv_data.get('professional_title', 'Professional')
        domain = cv_data.get('domain', '')
        parts.append(f"{title} in {domain}" if domain else title)
        
        # Skills summary
        skills = cv_data.get('skills', [])
        if skills:
            parts.append(f"Skills: {', '.join(skills[:15])}")
        
        # Career level
        level = cv_data.get('career_level', '')
        if level:
            parts.append(f"Experience level: {level}")
        
        return ". ".join(parts)
    
    def match(self, cv_data: Dict, job: Dict) -> float:
        """
        Calculate semantic similarity using BERT embeddings.
        """
        if not self.model:
            return 0.0
        
        try:
            # Build texts
            cv_text = self._build_profile_text(cv_data)
            job_text = f"{job.get('title', '')}. {job.get('description', '')[:2000]}"
            
            if not cv_text or not job_text:
                return 0.0
            
            # Encode
            cv_embedding = self.model.encode(cv_text, convert_to_numpy=True)
            job_embedding = self.model.encode(job_text, convert_to_numpy=True)
            
            # Cosine similarity
            similarity = np.dot(cv_embedding, job_embedding) / (
                np.linalg.norm(cv_embedding) * np.linalg.norm(job_embedding)
            )
            
            return round(float(similarity) * 100, 2)
            
        except Exception as e:
            print(f"BERT matching error: {e}")
            return 0.0


class AzureSemanticMatcher(BaseMatcher):
    """Azure OpenAI semantic matcher (if API key available)."""
    
    def __init__(self, api_key: str = None, endpoint: str = None):
        self.api_key = api_key or os.getenv("AZURE_OPENAI_API_KEY")
        self.endpoint = endpoint or os.getenv("AZURE_OPENAI_ENDPOINT")
        self.deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", "text-embedding-3-small")
        self.client = None
        
        if self.api_key and self.endpoint:
            try:
                from openai import AzureOpenAI
                self.client = AzureOpenAI(
                    api_key=self.api_key,
                    api_version="2024-02-01",
                    azure_endpoint=self.endpoint
                )
            except ImportError:
                pass
    
    def _get_embedding(self, text: str) -> Optional[List[float]]:
        """Get embedding from Azure OpenAI."""
        if not self.client:
            return None
        
        try:
            response = self.client.embeddings.create(
                input=[text[:8000]],  # Token limit
                model=self.deployment
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Azure embedding error: {e}")
            return None
    
    def match(self, cv_data: Dict, job: Dict) -> float:
        """Calculate match using Azure embeddings."""
        # Build safe texts (no PII)
        skills = cv_data.get('skills', [])
        cv_text = f"Professional with skills: {', '.join(skills[:20])}"
        
        job_text = f"Job: {job.get('title', '')}. Description: {job.get('description', '')[:2000]}"
        
        cv_emb = self._get_embedding(cv_text)
        job_emb = self._get_embedding(job_text)
        
        if cv_emb and job_emb:
            similarity = np.dot(cv_emb, job_emb) / (
                np.linalg.norm(cv_emb) * np.linalg.norm(job_emb)
            )
            return round(float(similarity) * 100, 2)
        
        return 0.0


class DynamicJobMatcher:
    """
    Orchestrator that combines multiple matching strategies.
    Automatically selects best available matcher.
    """
    
    def __init__(self, cv_data: Dict, match_mode: str = "auto"):
        self.cv_data = cv_data
        self.match_mode = match_mode
        
        # Initialize matchers
        self.tfidf_matcher = DynamicTFIDFMatcher()
        self.bert_matcher = None
        self.azure_matcher = None
        
        # Auto-detect best available
        if match_mode == "auto":
            match_mode = self._detect_best_mode()
        
        if match_mode in ["bert", "hybrid"]:
            self.bert_matcher = BertSemanticMatcher()
        
        if match_mode in ["azure", "hybrid"]:
            self.azure_matcher = AzureSemanticMatcher()
        
        self.active_mode = match_mode
    
    def _detect_best_mode(self) -> str:
        """Auto-detect best available matching mode."""
        # Try Azure first
        if os.getenv("AZURE_OPENAI_API_KEY"):
            return "hybrid"
        
        # Try BERT
        try:
            from sentence_transformers import SentenceTransformer
            return "bert"
        except ImportError:
            pass
        
        # Fallback to TF-IDF
        return "tfidf"
    
    def score_jobs(self, jobs: List[Dict], progress_callback=None) -> List[Dict]:
        """
        Score all jobs and return sorted results.
        """
        total = len(jobs)
        scored_jobs = []
        
        for i, job in enumerate(jobs):
            if progress_callback:
                progress_callback((i + 1) / total, f"🎯 Matching job {i+1}/{total}...")
            
            # Calculate scores from all available matchers
            scores = {}
            
            # Always have TF-IDF
            scores['tfidf'] = self.tfidf_matcher.match(self.cv_data, job)
            
            # BERT if available
            if self.bert_matcher:
                scores['bert'] = self.bert_matcher.match(self.cv_data, job)
            
            # Azure if available
            if self.azure_matcher:
                scores['azure'] = self.azure_matcher.match(self.cv_data, job)
            
            # Calculate weighted final score
            final_score = self._calculate_final_score(scores)
            
            job["Match Score"] = round(final_score, 2)
            job["_match_details"] = scores
            job["_match_mode"] = self.active_mode
            scored_jobs.append(job)
        
        # Sort by score (descending)
        scored_jobs.sort(key=lambda x: x.get("Match Score", 0), reverse=True)
        return scored_jobs
    
    def _calculate_final_score(self, scores: Dict[str, float]) -> float:
        """Calculate weighted final score based on available methods."""
        
        if not scores:
            return 0.0
        
        # If only TF-IDF available
        if len(scores) == 1 and 'tfidf' in scores:
            return scores['tfidf']
        
        # Hybrid weighting
        weights = {'tfidf': 0.2}
        
        if 'bert' in scores and scores['bert'] > 0:
            weights['bert'] = 0.5
        
        if 'azure' in scores and scores['azure'] > 0:
            weights['azure'] = 0.3
        
        # Normalize weights
        total_weight = sum(weights.values())
        normalized_weights = {k: v / total_weight for k, v in weights.items()}
        
        # Calculate weighted score
        final = sum(scores.get(k, 0) * normalized_weights.get(k, 0) for k in scores)
        
        return min(final, 100)


# Backward compatibility
class JobMatcher(DynamicJobMatcher):
    """Backward-compatible wrapper."""
    pass
