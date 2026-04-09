"""
LLM-Based CV Extractor - Dynamic Skill Extraction
Uses Azure OpenAI or local LLM to extract skills, experience, domain from sanitized CV text.
"""
import os
import json
from typing import List, Dict, Optional, Literal
from dataclasses import dataclass, field
from enum import Enum


class ExperienceLevel(str, Enum):
    ENTRY = "entry"
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"
    LEAD = "lead"
    EXECUTIVE = "executive"


@dataclass
class ExtractedSkill:
    """Individual skill with metadata."""
    name: str
    category: str  # e.g., "technical", "soft_skill", "domain_knowledge", "tool"
    years_experience: Optional[int] = None
    proficiency: Optional[Literal["beginner", "intermediate", "advanced", "expert"]] = None
    context: Optional[str] = None  # How it was mentioned in CV


@dataclass
class ExtractedExperience:
    """Work experience entry."""
    role: str
    company: Optional[str] = None  # May be masked
    duration_months: Optional[int] = None
    is_relevant: bool = True
    key_achievements: List[str] = field(default_factory=list)


@dataclass
class CVExtractionResult:
    """Complete structured output from LLM extraction."""
    # Professional profile
    professional_title: Optional[str] = None
    career_level: Optional[ExperienceLevel] = None
    domain: Optional[str] = None  # e.g., "healthcare", "technology", "finance"
    industry: Optional[str] = None  # More specific
    
    # Skills (dynamic - no hardcoding)
    technical_skills: List[ExtractedSkill] = field(default_factory=list)
    soft_skills: List[ExtractedSkill] = field(default_factory=list)
    domain_knowledge: List[ExtractedSkill] = field(default_factory=list)
    tools_software: List[ExtractedSkill] = field(default_factory=list)
    
    # Experience
    total_years_experience: Optional[float] = None
    experiences: List[ExtractedExperience] = field(default_factory=list)
    
    # Job preferences (inferred)
    job_preferences: List[str] = field(default_factory=list)  # e.g., "remote", "hybrid", "senior role"
    
    # Metadata
    extraction_confidence: float = 0.0  # 0-1
    extraction_method: str = "llm"  # "llm", "local", "hybrid"
    raw_skills_text: Optional[str] = None  # Concatenated for matching


class LLMCVExtractor:
    """
    LLM-powered CV extractor using Azure OpenAI with structured outputs.
    PII is already sanitized before reaching this class.
    """
    
    def __init__(self, api_key: Optional[str] = None, endpoint: Optional[str] = None):
        self.api_key = api_key or os.getenv("AZURE_OPENAI_API_KEY")
        self.endpoint = endpoint or os.getenv("AZURE_OPENAI_ENDPOINT")
        self.deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini")
        self.client = None
        
        if self.api_key and self.endpoint:
            try:
                from openai import AzureOpenAI
                self.client = AzureOpenAI(
                    api_key=self.api_key,
                    api_version="2024-08-01-preview",  # Required for structured outputs
                    azure_endpoint=self.endpoint
                )
            except ImportError:
                print("Azure OpenAI not available. LLM extraction disabled.")
    
    def _build_extraction_prompt(self, sanitized_text: str) -> str:
        """
        Build the extraction prompt.
        Text is already sanitized (no PII).
        """
        return f"""You are an expert CV analyzer. Extract professional information from the following CV text.

IMPORTANT:
- All personal identifiers (names, emails, phones) have been replaced with tokens like [EMAIL_1], [NAME_1]
- DO NOT extract or return these tokens as skills
- Focus ONLY on professional capabilities, skills, and experience
- Extract skills dynamically - there is NO predefined list
- Be comprehensive but accurate

CV TEXT:
---
{sanitized_text[:4000]}  # Limit to prevent token overflow
---

Extract and return a JSON object with this structure:
{{
    "professional_title": "EXACT job title as stated in CV header or summary. ONLY infer if no explicit title found.",
    "career_level": "one of: entry, junior, mid, senior, lead, executive",
    "domain": "broad domain like 'technology', 'healthcare', 'finance', 'education'",
    "industry": "specific industry if clear",
    "total_years_experience": number or null,
    
    "technical_skills": [
        {{
            "name": "skill name",
            "years_experience": number or null,
            "proficiency": "beginner|intermediate|advanced|expert",
            "context": "brief context from CV"
        }}
    ],
    "soft_skills": [same structure],
    "domain_knowledge": [same structure - industry-specific knowledge],
    "tools_software": [same structure - tools, software, platforms],
    
    "key_experiences": [
        {{
            "role": "job title",
            "duration_months": number or null,
            "key_achievements": ["achievement 1", "achievement 2"]
        }}
    ],
    
    "job_preferences": ["remote", "senior role", etc.],
    "extraction_confidence": 0.0-1.0
}}

Guidelines:
1. professional_title: PRIORITY 1 - Look for explicit title in CV header (e.g., "Senior Physiotherapist", "Software Engineer"). Use EXACT wording. PRIORITY 2 - If no explicit title, infer from current/most recent job role.
2. career_level: Based on years, seniority terms, scope of responsibilities
3. technical_skills: Programming languages, frameworks, technical methodologies
4. soft_skills: Communication, leadership, problem-solving, etc.
5. domain_knowledge: Industry-specific expertise (e.g., "HIPAA compliance", "financial auditing")
6. tools_software: Software, platforms, equipment mentioned
7. Do NOT make up skills - only extract what is genuinely mentioned or strongly implied
8. Return valid JSON only, no markdown formatting"""

    def _parse_llm_response(self, response_text: str) -> CVExtractionResult:
        """Parse LLM JSON response into structured dataclass."""
        try:
            # Clean up response - sometimes LLM wraps in markdown
            cleaned = response_text.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()
            
            data = json.loads(cleaned)
            
            # Build result
            result = CVExtractionResult(
                professional_title=data.get("professional_title"),
                career_level=data.get("career_level"),
                domain=data.get("domain"),
                industry=data.get("industry"),
                total_years_experience=data.get("total_years_experience"),
                job_preferences=data.get("job_preferences", []),
                extraction_confidence=data.get("extraction_confidence", 0.5),
                extraction_method="llm"
            )
            
            # Parse skills
            for category_key, category_name in [
                ("technical_skills", "technical"),
                ("soft_skills", "soft_skill"),
                ("domain_knowledge", "domain_knowledge"),
                ("tools_software", "tool")
            ]:
                for skill_data in data.get(category_key, []):
                    skill = ExtractedSkill(
                        name=skill_data.get("name", ""),
                        category=category_name,
                        years_experience=skill_data.get("years_experience"),
                        proficiency=skill_data.get("proficiency"),
                        context=skill_data.get("context")
                    )
                    if skill.name:  # Only add if name exists
                        if category_name == "technical":
                            result.technical_skills.append(skill)
                        elif category_name == "soft_skill":
                            result.soft_skills.append(skill)
                        elif category_name == "domain_knowledge":
                            result.domain_knowledge.append(skill)
                        elif category_name == "tool":
                            result.tools_software.append(skill)
            
            # Parse experiences
            for exp_data in data.get("key_experiences", []):
                exp = ExtractedExperience(
                    role=exp_data.get("role", ""),
                    duration_months=exp_data.get("duration_months"),
                    key_achievements=exp_data.get("key_achievements", [])
                )
                if exp.role:
                    result.experiences.append(exp)
            
            # Build raw skills text for matching
            all_skill_names = []
            for skills_list in [result.technical_skills, result.domain_knowledge, 
                               result.tools_software, result.soft_skills]:
                all_skill_names.extend([s.name for s in skills_list])
            result.raw_skills_text = ", ".join(all_skill_names)
            
            return result
            
        except json.JSONDecodeError as e:
            print(f"Failed to parse LLM response: {e}")
            print(f"Raw response: {response_text[:500]}...")
            return CVExtractionResult(
                extraction_confidence=0.0,
                extraction_method="llm_failed"
            )
    
    def extract(self, sanitized_text: str) -> CVExtractionResult:
        """
        Main extraction method.
        
        Args:
            sanitized_text: CV text with PII already masked
            
        Returns:
            CVExtractionResult with structured data
        """
        if not self.client:
            return CVExtractionResult(
                extraction_confidence=0.0,
                extraction_method="no_llm_available"
            )
        
        try:
            prompt = self._build_extraction_prompt(sanitized_text)
            
            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a precise CV analyzer. Extract structured professional information. Respond with valid JSON only."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,  # Low temperature for consistency
                max_tokens=2000
            )
            
            response_text = response.choices[0].message.content
            return self._parse_llm_response(response_text)
            
        except Exception as e:
            print(f"LLM extraction error: {e}")
            return CVExtractionResult(
                extraction_confidence=0.0,
                extraction_method="llm_error"
            )


class HybridExtractor:
    """
    Hybrid approach: Try LLM first, fall back to local extraction if unavailable.
    """
    
    def __init__(self):
        self.llm_extractor = LLMCVExtractor()
        self.local_extractor = None  # Will implement if needed
    
    def extract(self, raw_text: str, sanitized_text: str) -> CVExtractionResult:
        """
        Extract using best available method.
        
        Args:
            raw_text: Original CV text (for local extraction)
            sanitized_text: Sanitized text (for LLM)
        """
        # Try LLM first
        if self.llm_extractor.client:
            result = self.llm_extractor.extract(sanitized_text)
            if result.extraction_confidence > 0.3:
                return result
        
        # Fall back to local extraction
        return self._local_fallback(raw_text)
    
    def _local_fallback(self, raw_text: str) -> CVExtractionResult:
        """
        Fallback extraction using local NLP if LLM unavailable.
        Uses spacy for NER and simple keyword extraction.
        """
        result = CVExtractionResult(
            extraction_method="local_fallback",
            extraction_confidence=0.3  # Lower confidence for local
        )
        
        try:
            import spacy
            try:
                nlp = spacy.load("en_core_web_sm")
            except (ImportError, OSError):
                return result  # spaCy model not available, return empty result
            doc = nlp(raw_text.lower())
            
            # Extract noun phrases as potential skills
            noun_chunks = [chunk.text for chunk in doc.noun_chunks 
                          if len(chunk.text) > 3 and len(chunk.text) < 30]
            
            # Deduplicate and create skills
            seen = set()
            for chunk in noun_chunks[:50]:  # Limit
                clean = chunk.strip()
                if clean not in seen and not any(pii in clean for pii in ['@', 'http', 'phone', 'email']):
                    seen.add(clean)
                    skill = ExtractedSkill(
                        name=clean,
                        category="domain_knowledge",
                        context="extracted from noun phrase"
                    )
                    result.domain_knowledge.append(skill)
            
            result.raw_skills_text = ", ".join(seen)
            
            # Detect years of experience
            years_pattern = re.compile(r'(\d+)\+?\s*years?\s+(?:of\s+)?experience')
            matches = years_pattern.findall(raw_text.lower())
            if matches:
                result.total_years_experience = max(int(m) for m in matches)
            
        except Exception as e:
            print(f"Local extraction failed: {e}")
        
        return result
