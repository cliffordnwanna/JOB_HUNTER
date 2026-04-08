import io
import re
from typing import Dict, List, Set
import pdfplumber
from docx import Document

class EnhancedCVParser:
    """Advanced CV parser with comprehensive skill extraction."""

    def __init__(self):
        self.cv_data = {}
        self.skill_database = {
            'azure_ai': [
                'azure ai', 'azure ai foundry', 'azure openai', 'azure machine learning', 'azure search',
                'vector search', 'rag', 'embeddings', 'prompt engineering', 'copilot',
                'azure synapse', 'azure functions', 'azure cognitive services'
            ],
            'ai_ml': [
                'python', 'machine learning', 'deep learning', 'nlp', 'natural language processing',
                'computer vision', 'llm', 'large language models', 'langchain', 'llamaindex',
                'tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy', 'scipy', 'matplotlib'
            ],
            'engineering': [
                'software engineering', 'web development', 'frontend', 'backend', 'full stack',
                'react', 'angular', 'vue', 'node.js', 'express', 'django', 'flask', 'fastapi',
                'typescript', 'html', 'css', 'sass', 'tailwind', 'bootstrap',
                'mongodb', 'postgresql', 'mysql', 'redis', 'graphql', 'rest api',
                'ci/cd', 'jenkins', 'terraform', 'ansible', 'linux', 'devops',
                'microservices', 'system design', 'architecture', 'testing', 'unit testing'
            ],
            'data_science': [
                'sql', 'data analysis', 'data science', 'statistics', 'probability',
                'tableau', 'power bi', 'git', 'github', 'agile', 'scrum'
            ]
        }

    def parse_pdf(self, file_content: bytes) -> str:
        try:
            with pdfplumber.open(io.BytesIO(file_content)) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text() or ""
                return text
        except Exception as e:
            raise ValueError(f"PDF parsing error: {str(e)}")

    def parse_docx(self, file_content: bytes) -> str:
        try:
            doc = Document(io.BytesIO(file_content))
            return "\n".join([para.text for para in doc.paragraphs])
        except Exception as e:
            raise ValueError(f"DOCX parsing error: {str(e)}")

    def parse_txt(self, file_content: bytes) -> str:
        try:
            return file_content.decode('utf-8')
        except Exception as e:
            raise ValueError(f"TXT parsing error: {str(e)}")

    def extract_comprehensive_skills(self, text: str) -> Set[str]:
        if not isinstance(text, str):
            text = str(text)
        text_lower = text.lower()
        found_skills = set()

        all_skills = []
        for category in self.skill_database.values():
            all_skills.extend(category)

        for skill in all_skills:
            if skill in text_lower:
                found_skills.add(skill)

        prog_langs = ['python', 'java', 'javascript', 'r', 'sql', 'scala', 'c++', 'c#']
        for lang in prog_langs:
            if lang in text_lower:
                found_skills.add(lang)

        return found_skills

    def extract_info(self, text: str) -> Dict:
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)

        phone_pattern = r'[\+]?[(]?[0-9]{1,4}[)]?[-\s\.]?[(]?[0-9]{1,4}[)]?[-\s\.]?[0-9]{1,9}'
        phones = re.findall(phone_pattern, text)

        found_skills = self.extract_comprehensive_skills(text)
        years_exp = self._extract_years_experience(text)

        return {
            'email': emails[0] if emails else 'Not found',
            'phone': phones[0] if phones else 'Not found',
            'skills': sorted(list(found_skills)),
            'years_experience': years_exp,
            'full_text': text,
            'skill_count': len(found_skills)
        }

    def _extract_years_experience(self, text: str) -> int:
        text_lower = text.lower()
        years = 0

        patterns = [
            r'(\d+)\+?\s*years?\s+(?:of\s+)?experience',
            r'experience[:\s]+(\d+)\+?\s*years?',
            r'(\d+)\+?\s*years?\s+(?:in|working|as)',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text_lower)
            if matches:
                years = max(years, max([int(m) for m in matches]))

        date_pattern = r'(20\d{2}|19\d{2})\s*[-–—]\s*(20\d{2}|19\d{2}|present|current)'
        date_ranges = re.findall(date_pattern, text_lower)

        if date_ranges:
            total_years = 0
            for start, end in date_ranges:
                start_year = int(start)
                end_year = 2026 if end in ['present', 'current'] else int(end)
                total_years += (end_year - start_year)
            years = max(years, total_years)

        return years

    def parse(self, filename: str, file_content: bytes) -> Dict:
        ext = filename.lower().split('.')[-1]
        if ext == 'pdf':
            text = self.parse_pdf(file_content)
        elif ext in ['docx', 'doc']:
            text = self.parse_docx(file_content)
        elif ext == 'txt':
            text = self.parse_txt(file_content)
        else:
            raise ValueError(f"Unsupported format: {ext}")

        self.cv_data = self.extract_info(text)
        return self.cv_data
