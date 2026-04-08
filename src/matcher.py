import os
from typing import Dict, List, Set, Optional
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class BaseMatcher:
    """Base class for matching logic to ensure extensibility."""
    def match(self, cv_data: Dict, job: Dict) -> float:
        raise NotImplementedError

class TFIDFMatcher(BaseMatcher):
    """Fast, reliable TF-IDF based matching."""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words="english", max_features=1000, ngram_range=(1, 2))
        self.skill_synonyms = {
            "python": ["programming", "coding", "development"],
            "javascript": ["js", "frontend", "web development"],
            "react": ["frontend", "ui development", "web app"],
            "sql": ["database", "data", "queries"],
            "azure": ["cloud", "microsoft cloud", "azure ai"],
            "machine learning": ["ml", "ai", "artificial intelligence"]
        }

    def expand_skills(self, skills: Set[str]) -> Set[str]:
        expanded = set(skills)
        for skill in skills:
            if skill.lower() in self.skill_synonyms:
                expanded.update(self.skill_synonyms[skill.lower()])
        return expanded

    def match(self, cv_data: Dict, job: Dict) -> float:
        title = job.get("title", "").lower()
        desc = job.get("description", "")[:1500].lower()
        cv_text = " ".join(cv_data.get("skills", [])) + " " + cv_data.get("full_text", "")[:3000].lower()
        
        # TF-IDF Score
        try:
            vectors = self.vectorizer.fit_transform([cv_text, f"{title} {title} {desc}"])
            tfidf_score = float(cosine_similarity(vectors[0:1], vectors[1:2])[0][0]) * 100
        except Exception:
            tfidf_score = 0.0

        # Skill Matching
        cv_skills = set(s.lower() for s in cv_data.get("skills", []))
        expanded_skills = self.expand_skills(cv_skills)
        job_text = f"{title} {desc}"
        skill_matches = sum(1 for s in expanded_skills if s in job_text)
        skill_score = min((skill_matches / max(len(cv_skills), 1)) * 100, 100)

        # Final Score (Weighted)
        final_score = (tfidf_score * 0.4) + (skill_score * 0.6)
        return round(min(final_score, 100), 2)

class AzureSemanticMatcher(BaseMatcher):
    """
    Advanced Semantic Matcher using Azure OpenAI Embeddings.
    This demonstrates RAG (Retrieval-Augmented Generation) patterns.
    """
    
    def __init__(self, api_key: str = None, endpoint: str = None, deployment_name: str = "text-embedding-3-small"):
        self.api_key = api_key or os.getenv("AZURE_OPENAI_API_KEY")
        self.endpoint = endpoint or os.getenv("AZURE_OPENAI_ENDPOINT")
        self.deployment_name = deployment_name
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
                print("OpenAI library not installed. Semantic matching will be unavailable.")

    def get_embedding(self, text: str):
        if not self.client:
            return None
        try:
            response = self.client.embeddings.create(
                input=[text],
                model=self.deployment_name
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Azure OpenAI Error: {e}")
            return None

    def match(self, cv_data: Dict, job: Dict) -> float:
        if not self.client:
            return 0.0
            
        cv_text = cv_data.get("full_text", "")[:2000]
        job_text = f"Title: {job.get('title')}\nDescription: {job.get('description')[:2000]}"
        
        cv_emb = self.get_embedding(cv_text)
        job_emb = self.get_embedding(job_text)
        
        if cv_emb and job_emb:
            # Cosine similarity
            similarity = np.dot(cv_emb, job_emb) / (np.linalg.norm(cv_emb) * np.linalg.norm(job_emb))
            return round(similarity * 100, 2)
        return 0.0

class JobMatcher:
    """Orchestrator for matching jobs to CV."""
    
    def __init__(self, cv_data: Dict, use_azure: bool = False):
        self.cv_data = cv_data
        self.tfidf_matcher = TFIDFMatcher()
        self.azure_matcher = AzureSemanticMatcher() if use_azure else None

    def score_jobs(self, jobs: List[Dict], progress_callback=None) -> List[Dict]:
        total = len(jobs)
        for i, job in enumerate(jobs):
            if progress_callback:
                progress_callback((i + 1) / total, f"🎯 Matching job {i+1}/{total}...")
            
            # Use TF-IDF as base
            score = self.tfidf_matcher.match(self.cv_data, job)
            
            # Optionally augment with Azure Semantic Search
            if self.azure_matcher:
                semantic_score = self.azure_matcher.match(self.cv_data, job)
                if semantic_score > 0:
                    score = (score * 0.3) + (semantic_score * 0.7)
            
            job["Match Score"] = round(score, 2)
            
        # Sort by score
        return sorted(jobs, key=lambda x: x.get("Match Score", 0), reverse=True)
