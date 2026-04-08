# Enhanced CV Parser - Extracts significantly more skills and information
# Replace the CVParser class in your Colab notebook with this

import re
from typing import Dict, List, Set

class EnhancedCVParser:
    """Advanced CV parser with comprehensive skill extraction."""
    
    def __init__(self):
        self.cv_data = {}
        
        # Comprehensive skill databases for different roles
        self.skill_database = {
            # Social Media Manager Skills
            'social_media': [
                'instagram', 'facebook', 'twitter', 'tiktok', 'linkedin', 'youtube',
                'snapchat', 'pinterest', 'social media management', 'content creation',
                'content strategy', 'community management', 'social media marketing',
                'social media analytics', 'engagement', 'brand awareness', 'influencer marketing',
                'social media advertising', 'paid social', 'organic social', 'hashtag strategy',
                'social listening', 'crisis management', 'brand voice', 'copywriting',
                'content calendar', 'scheduling', 'hootsuite', 'buffer', 'sprout social',
                'later', 'meta business suite', 'facebook ads manager', 'instagram insights',
                'twitter analytics', 'tiktok analytics', 'canva', 'adobe creative suite',
                'photoshop', 'illustrator', 'video editing', 'premiere pro', 'final cut',
                'capcut', 'seo', 'sem', 'google analytics', 'social media reporting',
                'kpi tracking', 'roi analysis', 'a/b testing', 'audience insights',
                'social media strategy', 'brand management', 'reputation management'
            ],
            
            # Data Science / AI Engineer Skills
            'data_science': [
                'python', 'r', 'sql', 'java', 'scala', 'javascript', 'c++',
                'machine learning', 'deep learning', 'neural networks', 'ai', 'artificial intelligence',
                'natural language processing', 'nlp', 'computer vision', 'cv',
                'data analysis', 'data science', 'statistics', 'probability',
                'linear algebra', 'calculus', 'optimization', 'algorithms',
                'tensorflow', 'pytorch', 'keras', 'scikit-learn', 'sklearn',
                'pandas', 'numpy', 'scipy', 'matplotlib', 'seaborn', 'plotly',
                'jupyter', 'apache spark', 'hadoop', 'big data', 'etl',
                'data engineering', 'data pipeline', 'airflow', 'kafka',
                'sql server', 'postgresql', 'mysql', 'mongodb', 'nosql',
                'aws', 'azure', 'gcp', 'google cloud', 'cloud computing',
                'docker', 'kubernetes', 'mlops', 'model deployment',
                'feature engineering', 'data visualization', 'tableau', 'power bi',
                'predictive modeling', 'classification', 'regression', 'clustering',
                'time series', 'forecasting', 'recommendation systems',
                'transformers', 'bert', 'gpt', 'llm', 'large language models',
                'reinforcement learning', 'supervised learning', 'unsupervised learning',
                'data mining', 'data wrangling', 'exploratory data analysis', 'eda',
                'hypothesis testing', 'experiment design', 'causal inference',
                'git', 'github', 'version control', 'agile', 'scrum'
            ],
            
            # Common soft skills
            'soft_skills': [
                'communication', 'teamwork', 'leadership', 'project management',
                'problem solving', 'critical thinking', 'creativity', 'collaboration',
                'time management', 'organization', 'adaptability', 'remote work',
                'agile', 'scrum', 'cross-functional', 'stakeholder management',
                'presentation', 'writing', 'research', 'analytical'
            ]
        }
    
    def parse_pdf(self, file_content):
        """Extract text from PDF."""
        import io
        import pdfplumber
        try:
            with pdfplumber.open(io.BytesIO(file_content)) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text() or ""
                return text
        except Exception as e:
            raise ValueError(f"PDF parsing error: {str(e)}")
    
    def parse_docx(self, file_content):
        """Extract text from DOCX."""
        import io
        from docx import Document
        try:
            doc = Document(io.BytesIO(file_content))
            return "\n".join([para.text for para in doc.paragraphs])
        except Exception as e:
            raise ValueError(f"DOCX parsing error: {str(e)}")
    
    def parse_txt(self, file_content):
        """Extract text from TXT."""
        try:
            return file_content.decode('utf-8')
        except Exception as e:
            raise ValueError(f"TXT parsing error: {str(e)}")
    
    def extract_comprehensive_skills(self, text: str) -> Set[str]:
        """Extract skills using multiple methods."""
        text_lower = text.lower()
        found_skills = set()
        
        # Method 1: Exact matches from skill database
        all_skills = (
            self.skill_database['social_media'] + 
            self.skill_database['data_science'] + 
            self.skill_database['soft_skills']
        )
        
        for skill in all_skills:
            # Word boundary matching to avoid false positives
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text_lower):
                found_skills.add(skill)
        
        # Method 2: Extract from common CV sections
        sections = self._extract_sections(text)
        
        # Skills section often has bullet points or commas
        if 'skills' in sections:
            skills_text = sections['skills']
            # Split by common delimiters
            potential_skills = re.split(r'[,;•\n\-]', skills_text)
            for skill in potential_skills:
                skill = skill.strip().lower()
                if len(skill) > 2 and skill in text_lower:
                    # Check if it's in our skill database
                    for db_skill in all_skills:
                        if db_skill in skill or skill in db_skill:
                            found_skills.add(db_skill)
        
        # Method 3: Pattern-based extraction
        # Extract programming languages
        prog_langs = ['python', 'java', 'javascript', 'r', 'sql', 'scala', 'c++', 'c#']
        for lang in prog_langs:
            if re.search(r'\b' + lang + r'\b', text_lower):
                found_skills.add(lang)
        
        # Extract tools with version numbers (e.g., "Python 3.9", "TensorFlow 2.0")
        tool_pattern = r'(python|java|sql|tensorflow|pytorch|tableau|power bi|aws|azure|gcp)\s*\d*\.?\d*'
        matches = re.findall(tool_pattern, text_lower)
        found_skills.update(matches)
        
        return found_skills
    
    def _extract_sections(self, text: str) -> Dict[str, str]:
        """Extract common CV sections."""
        text_lower = text.lower()
        sections = {}
        
        # Common section headers
        headers = {
            'skills': r'(?:technical\s+)?skills?|competencies|expertise',
            'experience': r'(?:work\s+)?experience|employment|professional\s+experience',
            'education': r'education|academic|qualifications',
            'summary': r'summary|profile|objective|about\s+me'
        }
        
        for section_name, pattern in headers.items():
            match = re.search(pattern, text_lower)
            if match:
                start = match.end()
                # Find next section or end of text
                next_section = len(text)
                for other_pattern in headers.values():
                    next_match = re.search(other_pattern, text_lower[start:])
                    if next_match:
                        next_section = min(next_section, start + next_match.start())
                
                sections[section_name] = text[start:next_section]
        
        return sections
    
    def extract_info(self, text: str) -> Dict:
        """Extract structured information from CV text."""
        
        # Extract email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        
        # Extract phone
        phone_pattern = r'[\+]?[(]?[0-9]{1,4}[)]?[-\s\.]?[(]?[0-9]{1,4}[)]?[-\s\.]?[0-9]{1,9}'
        phones = re.findall(phone_pattern, text)
        
        # Extract comprehensive skills
        found_skills = self.extract_comprehensive_skills(text)
        
        # Extract years of experience (multiple patterns)
        years_exp = self._extract_years_experience(text)
        
        # Categorize skills
        categorized_skills = self._categorize_skills(found_skills)
        
        # Extract education level
        education = self._extract_education(text)
        
        return {
            'email': emails[0] if emails else 'Not found',
            'phone': phones[0] if phones else 'Not found',
            'skills': sorted(list(found_skills)),
            'years_experience': years_exp,
            'full_text': text,
            'skill_count': len(found_skills),
            'categorized_skills': categorized_skills,
            'education': education,
            'skill_categories': {
                'technical': len(categorized_skills.get('technical', [])),
                'tools': len(categorized_skills.get('tools', [])),
                'soft': len(categorized_skills.get('soft', []))
            }
        }
    
    def _extract_years_experience(self, text: str) -> int:
        """Extract years of experience using multiple patterns."""
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
        
        # Alternative: Calculate from date ranges in experience section
        date_pattern = r'(20\d{2}|19\d{2})\s*[-–—]\s*(20\d{2}|19\d{2}|present|current)'
        date_ranges = re.findall(date_pattern, text_lower)
        
        if date_ranges:
            total_years = 0
            for start, end in date_ranges:
                start_year = int(start)
                end_year = 2025 if end in ['present', 'current'] else int(end)
                total_years += (end_year - start_year)
            years = max(years, total_years)
        
        return years
    
    def _categorize_skills(self, skills: Set[str]) -> Dict[str, List[str]]:
        """Categorize skills into technical, tools, and soft skills."""
        categories = {
            'technical': [],
            'tools': [],
            'soft': []
        }
        
        tools = ['canva', 'photoshop', 'tableau', 'power bi', 'hootsuite', 'buffer', 
                'tensorflow', 'pytorch', 'jupyter', 'git', 'docker', 'aws', 'azure']
        
        for skill in skills:
            if skill in self.skill_database['soft_skills']:
                categories['soft'].append(skill)
            elif any(tool in skill for tool in tools):
                categories['tools'].append(skill)
            else:
                categories['technical'].append(skill)
        
        return categories
    
    def _extract_education(self, text: str) -> str:
        """Extract highest education level."""
        text_lower = text.lower()
        
        if 'phd' in text_lower or 'ph.d' in text_lower or 'doctorate' in text_lower:
            return 'PhD'
        elif 'master' in text_lower or 'msc' in text_lower or 'm.s.' in text_lower:
            return 'Master\'s'
        elif 'bachelor' in text_lower or 'bsc' in text_lower or 'b.s.' in text_lower:
            return 'Bachelor\'s'
        else:
            return 'Not specified'
    
    def parse(self, filename: str, file_content: bytes) -> Dict:
        """Main parsing function."""
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

# Usage example (replace in your main code)
# parser = EnhancedCVParser()
# cv_data = parser.parse(filename, file_content)





# HTML Cleaner for Job Descriptions
# Add this to your Colab notebook

from bs4 import BeautifulSoup
import re

class DescriptionCleaner:
    """Clean and format job descriptions."""
    
    @staticmethod
    def clean_html(html_text: str, max_length: int = 500) -> str:
        """
        Remove HTML tags and clean text for readability.
        
        Args:
            html_text: Raw HTML string
            max_length: Maximum character length (default 500)
            
        Returns:
            Clean, human-readable text
        """
        if not html_text:
            return "No description available"
        
        # Parse HTML
        soup = BeautifulSoup(html_text, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text
        text = soup.get_text()
        
        # Break into lines and remove leading/trailing space
        lines = (line.strip() for line in text.splitlines())
        
        # Break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        
        # Drop blank lines
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Remove common HTML artifacts
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&amp;', '&')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&quot;', '"')
        
        # Truncate if too long
        if len(text) > max_length:
            text = text[:max_length].rsplit(' ', 1)[0] + '...'
        
        return text
    
    @staticmethod
    def extract_key_requirements(description: str) -> List[str]:
        """Extract key requirements from job description."""
        requirements = []
        desc_lower = description.lower()
        
        # Common requirement patterns
        patterns = [
            r'(?:required|must have|need)[:\s]+([^.;]+)',
            r'(?:experience with|knowledge of)[:\s]+([^.;]+)',
            r'(?:proficiency in|expertise in)[:\s]+([^.;]+)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, desc_lower)
            requirements.extend(matches)
        
        return requirements[:5]  # Top 5 requirements
    
    @staticmethod
    def format_for_display(job_dict: Dict) -> str:
        """Format job for console display."""
        clean_desc = DescriptionCleaner.clean_html(job_dict.get('Description', ''))
        
        output = f"""
{'='*70}
🎯 {job_dict['Title']} at {job_dict['Company']}
{'='*70}
📍 Location: {job_dict['Location']}
💰 Salary: {job_dict['Salary']}
📅 Posted: {job_dict['Posted']}
🔗 URL: {job_dict['URL']}
⭐ Match Score: {job_dict['Match Score']}%
📊 {job_dict['Match Explanation']}

📝 Description:
{clean_desc}

"""
        return output

# Integration with your main code
def clean_job_descriptions(jobs_df):
    """Apply cleaning to all job descriptions in DataFrame."""
    cleaner = DescriptionCleaner()
    
    print("🧹 Cleaning job descriptions...")
    jobs_df['Description'] = jobs_df['Description'].apply(
        lambda x: cleaner.clean_html(x, max_length=300)
    )
    
    print("✅ Descriptions cleaned!")
    return jobs_df

# Usage in your main workflow:
# After matching, add this line:
# jobs_df = clean_job_descriptions(jobs_df)



# Advanced Job Filter - Recency and Relevance
# Add this to your Colab notebook

from datetime import datetime, timedelta
from typing import List, Dict
import pandas as pd

class JobFilter:
    """Filter jobs based on recency, relevance, and quality."""
    
    def __init__(self, preferences: Dict):
        self.preferences = preferences
        self.now = datetime.now()
    
    def parse_date(self, date_str: str) -> datetime:
        """Parse various date formats to datetime."""
        if not date_str or date_str == 'N/A' or date_str == 'Recent':
            return self.now  # Assume recent if no date
        
        try:
            # ISO format (2025-12-28T00:00:00)
            if 'T' in date_str:
                return datetime.fromisoformat(date_str.replace('+00:00', ''))
            # Date only (2025-12-28)
            else:
                return datetime.strptime(date_str[:10], '%Y-%m-%d')
        except:
            return self.now  # Default to now if parsing fails
    
    def filter_by_recency(self, jobs_df: pd.DataFrame, max_days: int = 14) -> pd.DataFrame:
        """Filter jobs posted within last N days."""
        print(f"\n🗓️  Filtering jobs posted within last {max_days} days...")
        
        # Parse dates
        jobs_df['parsed_date'] = jobs_df['Posted'].apply(self.parse_date)
        
        # Calculate days ago
        jobs_df['days_ago'] = (self.now - jobs_df['parsed_date']).dt.days
        
        # Filter
        recent_jobs = jobs_df[jobs_df['days_ago'] <= max_days].copy()
        
        print(f"   Kept {len(recent_jobs)}/{len(jobs_df)} recent jobs")
        return recent_jobs
    
    def filter_by_minimum_score(self, jobs_df: pd.DataFrame, min_score: float = 50.0) -> pd.DataFrame:
        """Filter jobs with minimum match score."""
        print(f"\n⭐ Filtering jobs with minimum {min_score}% match...")
        
        filtered = jobs_df[jobs_df['Match Score'] >= min_score].copy()
        
        print(f"   Kept {len(filtered)}/{len(jobs_df)} high-quality matches")
        return filtered
    
    def filter_by_preferences(self, jobs_df: pd.DataFrame) -> pd.DataFrame:
        """Apply user preference filters."""
        print("\n⚙️  Applying preference filters...")
        
        filtered = jobs_df.copy()
        initial_count = len(filtered)
        
        # Remote only filter
        if self.preferences.get('remote_only', False):
            filtered = filtered[
                filtered['Location'].str.lower().str.contains('remote', na=False)
            ]
            print(f"   Remote filter: {len(filtered)}/{initial_count} jobs")
        
        # Job title filter (if specified)
        job_titles = self.preferences.get('job_titles', [])
        if job_titles:
            title_pattern = '|'.join(job_titles)
            filtered = filtered[
                filtered['Title'].str.lower().str.contains(title_pattern, case=False, na=False)
            ]
            print(f"   Title filter: {len(filtered)}/{initial_count} jobs")
        
        return filtered
    
    def detect_red_flags(self, job_row: pd.Series) -> List[str]:
        """Detect red flags in job posting."""
        red_flags = []
        desc_lower = str(job_row['Description']).lower()
        title_lower = str(job_row['Title']).lower()
        
        # Unpaid/internship
        if any(term in desc_lower or term in title_lower for term in ['unpaid', 'volunteer', 'internship']):
            red_flags.append('⚠️ Unpaid/Internship')
        
        # Commission only
        if 'commission only' in desc_lower or 'no base salary' in desc_lower:
            red_flags.append('⚠️ Commission-only')
        
        # MLM indicators
        mlm_terms = ['mlm', 'multi-level', 'unlimited earning', 'be your own boss', 'work from home opportunity']
        if any(term in desc_lower for term in mlm_terms):
            red_flags.append('🚨 Possible MLM')
        
        # Overly vague
        if len(job_row['Description']) < 100:
            red_flags.append('⚠️ Vague description')
        
        # Entry level requiring 5+ years
        if 'entry' in title_lower or 'junior' in title_lower:
            if any(term in desc_lower for term in ['5+ years', '7+ years', '10+ years']):
                red_flags.append('⚠️ Entry-level with senior requirements')
        
        return red_flags
    
    def add_red_flags(self, jobs_df: pd.DataFrame) -> pd.DataFrame:
        """Add red flag column to DataFrame."""
        print("\n🚨 Detecting red flags...")
        
        jobs_df['Red Flags'] = jobs_df.apply(self.detect_red_flags, axis=1)
        jobs_df['Has Red Flags'] = jobs_df['Red Flags'].apply(lambda x: len(x) > 0)
        
        flagged_count = jobs_df['Has Red Flags'].sum()
        print(f"   Found {flagged_count} jobs with red flags")
        
        return jobs_df
    
    def apply_all_filters(
        self, 
        jobs_df: pd.DataFrame, 
        max_days: int = 14,
        min_score: float = 50.0,
        exclude_red_flags: bool = True
    ) -> pd.DataFrame:
        """Apply all filters in sequence."""
        print("\n" + "="*70)
        print("🔍 APPLYING ADVANCED FILTERS")
        print("="*70)
        
        initial_count = len(jobs_df)
        
        # Step 1: Recency filter
        filtered = self.filter_by_recency(jobs_df, max_days)
        
        # Step 2: Minimum score filter
        filtered = self.filter_by_minimum_score(filtered, min_score)
        
        # Step 3: Preference filters
        filtered = self.filter_by_preferences(filtered)
        
        # Step 4: Add red flags (but don't exclude yet)
        filtered = self.add_red_flags(filtered)
        
        # Step 5: Optionally exclude red flags
        if exclude_red_flags:
            print("\n🚫 Excluding jobs with red flags...")
            clean_count = len(filtered[~filtered['Has Red Flags']])
            filtered = filtered[~filtered['Has Red Flags']].copy()
            print(f"   Kept {clean_count} clean jobs")
        
        # Final sort: by match score, then recency
        filtered = filtered.sort_values(
            by=['Match Score', 'days_ago'], 
            ascending=[False, True]
        ).reset_index(drop=True)
        
        print("\n" + "="*70)
        print(f"✅ FILTERING COMPLETE: {len(filtered)}/{initial_count} jobs passed")
        print("="*70 + "\n")
        
        return filtered

# Enhanced matching system with better scoring
class EnhancedJobMatcher:
    """Enhanced matcher with better scoring logic."""
    
    def __init__(self):
        print("🧠 Loading AI model for matching...")
        from sentence_transformers import SentenceTransformer, util
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.util = util
        print("✅ AI model loaded!")
    
    def calculate_match_score(self, cv_data: Dict, job: Dict, preferences: Dict) -> tuple:
        """Enhanced matching with better weights."""
        
        # Create enriched CV profile
        cv_skills = ' '.join(cv_data['skills'])
        cv_text = f"{cv_skills} {cv_data['full_text'][:1000]}"
        
        # Create enriched job profile
        job_title = job['title']
        job_desc = job['description'][:1000] if job['description'] else ''
        job_tags = ' '.join(job.get('tags', []))
        job_text = f"{job_title} {job_desc} {job_tags}"
        
        # Calculate semantic similarity (0-40 points)
        cv_embedding = self.model.encode(cv_text, convert_to_tensor=True)
        job_embedding = self.model.encode(job_text, convert_to_tensor=True)
        similarity = self.util.cos_sim(cv_embedding, job_embedding).item()
        base_score = similarity * 40
        
        # Hard skill matches (0-35 points) - MUCH MORE WEIGHT
        job_text_lower = job_text.lower()
        cv_skills_set = set(cv_data['skills'])
        
        # Count exact skill matches
        skill_matches = sum(1 for skill in cv_skills_set if skill in job_text_lower)
        
        # Weighted by importance
        total_cv_skills = len(cv_skills_set)
        if total_cv_skills > 0:
            skill_match_ratio = skill_matches / total_cv_skills
            skill_score = skill_match_ratio * 35
        else:
            skill_score = 0
        
        # Title match bonus (0-15 points)
        title_bonus = 0
        job_title_lower = job_title.lower()
        pref_titles = preferences.get('job_titles', [])
        
        for pref_title in pref_titles:
            if pref_title.lower() in job_title_lower:
                title_bonus = 15
                break
            # Partial match (e.g., "data" in "data analyst")
            elif any(word in job_title_lower for word in pref_title.lower().split()):
                title_bonus = 7
        
        # Preference match (0-10 points)
        pref_bonus = 0
        if preferences.get('remote_only') and 'remote' in job['location'].lower():
            pref_bonus += 5
        
        # Experience match (bonus/penalty)
        if 'years_experience' in cv_data and cv_data['years_experience'] > 0:
            job_exp_required = self._extract_years_requirement(job_desc)
            if job_exp_required > 0:
                if cv_data['years_experience'] >= job_exp_required:
                    pref_bonus += 5
        
        # Calculate final score
        final_score = min(base_score + skill_score + title_bonus + pref_bonus, 100)
        
        # Generate detailed explanation
        explanation = (
            f"Semantic: {similarity*100:.1f}% | "
            f"Skills: {skill_matches}/{total_cv_skills} | "
            f"Title match: {'✓' if title_bonus > 0 else '✗'} | "
            f"Remote: {'✓' if pref_bonus > 0 else '✗'}"
        )
        
        return final_score, explanation
    
    def _extract_years_requirement(self, description: str) -> int:
        """Extract years of experience required."""
        import re
        desc_lower = description.lower()
        
        patterns = [
            r'(\d+)\+?\s*years?\s+(?:of\s+)?experience',
            r'(\d+)\+?\s*years?\s+(?:in|working)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, desc_lower)
            if matches:
                return max([int(m) for m in matches])
        
        return 0

# Integration example:
# Replace JobMatcher in your code with EnhancedJobMatcher
# After matching, apply filters:
#
# filter = JobFilter(preferences)
# filtered_jobs = filter.apply_all_filters(
#     jobs_df, 
#     max_days=14,      # Last 2 weeks only
#     min_score=60.0,   # 60%+ match only
#     exclude_red_flags=True
# )

# Premium Job Sources Integration
# Add these to your JobScraper class

import requests
from bs4 import BeautifulSoup
import time
from typing import List, Dict

class PremiumJobSources:
    """Premium job board scrapers for high-quality listings."""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    # ==========================================
    # LINKEDIN JOBS (Highest Quality Source)
    # ==========================================
    
    def scrape_linkedin_jobs(self, keywords: str, location: str = 'Remote', limit: int = 25) -> List[Dict]:
        """
        Scrape LinkedIn Jobs using their public job search.
        Note: LinkedIn has rate limits, use sparingly.
        """
        print("  📡 Fetching from LinkedIn Jobs...")
        
        try:
            # LinkedIn's public job search URL
            base_url = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
            
            params = {
                'keywords': keywords,
                'location': location,
                'f_WT': '2',  # Remote filter (1=on-site, 2=remote, 3=hybrid)
                'start': 0
            }
            
            all_jobs = []
            
            # Get multiple pages (25 jobs per page)
            for page in range(0, min(limit // 25 + 1, 3)):  # Max 3 pages = 75 jobs
                params['start'] = page * 25
                
                response = requests.get(base_url, params=params, headers=self.headers, timeout=15)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    job_cards = soup.find_all('li')
                    
                    for card in job_cards[:limit]:
                        try:
                            # Extract job info
                            title_elem = card.find('h3', class_='base-search-card__title')
                            company_elem = card.find('h4', class_='base-search-card__subtitle')
                            location_elem = card.find('span', class_='job-search-card__location')
                            link_elem = card.find('a', class_='base-card__full-link')
                            date_elem = card.find('time')
                            
                            if title_elem and company_elem and link_elem:
                                job = {
                                    'title': title_elem.text.strip(),
                                    'company': company_elem.text.strip(),
                                    'location': location_elem.text.strip() if location_elem else 'Remote',
                                    'description': '',  # Need separate request for full description
                                    'tags': keywords.split(),
                                    'url': link_elem['href'].split('?')[0],  # Clean URL
                                    'salary': 'Not specified',
                                    'posted_date': date_elem['datetime'] if date_elem and date_elem.has_attr('datetime') else 'Recent',
                                    'source': 'LinkedIn'
                                }
                                all_jobs.append(job)
                        
                        except Exception:
                            continue
                    
                    # Be polite - wait between pages
                    if page < 2:
                        time.sleep(2)
                
                else:
                    print(f"    ⚠️ LinkedIn rate limit or error (status {response.status_code})")
                    break
            
            print(f"    ✅ Found {len(all_jobs)} jobs from LinkedIn")
            return all_jobs
        
        except Exception as e:
            print(f"    ⚠️ LinkedIn error: {str(e)}")
            return []
    
    # ==========================================
    # INDEED (Highest Volume Source)
    # ==========================================
    
    def scrape_indeed(self, keywords: str, location: str = 'Remote', limit: int = 50) -> List[Dict]:
        """
        Scrape Indeed jobs.
        Note: Indeed has strict anti-scraping. Consider using their API if available.
        """
        print("  📡 Fetching from Indeed...")
        
        try:
            base_url = "https://www.indeed.com/jobs"
            
            params = {
                'q': keywords,
                'l': location,
                'sc': '0kf:attr(DSQF7);',  # Remote jobs filter
                'sort': 'date'  # Sort by date
            }
            
            response = requests.get(base_url, params=params, headers=self.headers, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                jobs = []
                
                # Indeed uses div elements with specific classes
                job_cards = soup.find_all('div', class_='job_seen_beacon')[:limit]
                
                for card in job_cards:
                    try:
                        title_elem = card.find('h2', class_='jobTitle')
                        company_elem = card.find('span', class_='companyName')
                        location_elem = card.find('div', class_='companyLocation')
                        
                        if title_elem and company_elem:
                            # Get job link
                            link = title_elem.find('a')
                            job_id = link['data-jk'] if link and link.has_attr('data-jk') else ''
                            
                            job = {
                                'title': title_elem.text.strip(),
                                'company': company_elem.text.strip(),
                                'location': location_elem.text.strip() if location_elem else 'Remote',
                                'description': '',
                                'tags': keywords.split(),
                                'url': f"https://www.indeed.com/viewjob?jk={job_id}",
                                'salary': 'Not specified',
                                'posted_date': 'Recent',
                                'source': 'Indeed'
                            }
                            jobs.append(job)
                    
                    except Exception:
                        continue
                
                print(f"    ✅ Found {len(jobs)} jobs from Indeed")
                return jobs
            
            else:
                print(f"    ⚠️ Indeed returned status {response.status_code}")
                return []
        
        except Exception as e:
            print(f"    ⚠️ Indeed error: {str(e)}")
            return []
    
    # ==========================================
    # FLEXJOBS (Premium Remote Jobs)
    # ==========================================
    
    def scrape_flexjobs(self, keywords: str, limit: int = 30) -> List[Dict]:
        """
        Scrape FlexJobs (premium remote job board).
        Note: FlexJobs requires subscription for full access.
        """
        print("  📡 Fetching from FlexJobs...")
        
        try:
            # FlexJobs public search (limited results)
            base_url = "https://www.flexjobs.com/search"
            
            params = {
                'search': keywords,
                'location': 'remote'
            }
            
            response = requests.get(base_url, params=params, headers=self.headers, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                jobs = []
                
                job_listings = soup.find_all('div', class_='job')[:limit]
                
                for listing in job_listings:
                    try:
                        title_elem = listing.find('a', class_='job-title')
                        company_elem = listing.find('span', class_='company-name')
                        
                        if title_elem and company_elem:
                            job = {
                                'title': title_elem.text.strip(),
                                'company': company_elem.text.strip(),
                                'location': 'Remote',
                                'description': '',
                                'tags': keywords.split(),
                                'url': f"https://www.flexjobs.com{title_elem['href']}" if title_elem.has_attr('href') else '',
                                'salary': 'Not specified',
                                'posted_date': 'Recent',
                                'source': 'FlexJobs'
                            }
                            jobs.append(job)
                    
                    except Exception:
                        continue
                
                print(f"    ✅ Found {len(jobs)} jobs from FlexJobs")
                return jobs
            
            else:
                print(f"    ⚠️ FlexJobs returned status {response.status_code}")
                return []
        
        except Exception as e:
            print(f"    ⚠️ FlexJobs error: {str(e)}")
            return []
    
    # ==========================================
    # ANGEL LIST (Startup Jobs)
    # ==========================================
    
    def scrape_angellist(self, keywords: str, limit: int = 25) -> List[Dict]:
        """
        Scrape AngelList/Wellfound (startup jobs).
        """
        print("  📡 Fetching from AngelList/Wellfound...")
        
        try:
            # Note: AngelList recently rebranded to Wellfound
            base_url = "https://wellfound.com/jobs"
            
            params = {
                'q': keywords,
                'remote': 'true'
            }
            
            response = requests.get(base_url, params=params, headers=self.headers, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                jobs = []
                
                # AngelList structure varies, this is a basic implementation
                job_cards = soup.find_all('div', class_='job-card')[:limit]
                
                for card in job_cards:
                    try:
                        title_elem = card.find('h2')
                        company_elem = card.find('span', class_='company-name')
                        
                        if title_elem:
                            job = {
                                'title': title_elem.text.strip(),
                                'company': company_elem.text.strip() if company_elem else 'Startup',
                                'location': 'Remote',
                                'description': '',
                                'tags': ['startup'] + keywords.split(),
                                'url': '',  # Would need full URL parsing
                                'salary': 'Not specified',
                                'posted_date': 'Recent',
                                'source': 'AngelList'
                            }
                            jobs.append(job)
                    
                    except Exception:
                        continue
                
                print(f"    ✅ Found {len(jobs)} jobs from AngelList")
                return jobs
            
            else:
                print(f"    ⚠️ AngelList returned status {response.status_code}")
                return []
        
        except Exception as e:
            print(f"    ⚠️ AngelList error: {str(e)}")
            return []
    
    # ==========================================
    # MASTER SCRAPER
    # ==========================================
    
    def scrape_all_premium(self, keywords: str, location: str = 'Remote') -> List[Dict]:
        """
        Scrape all premium sources.
        
        Returns jobs from:
        - LinkedIn (25 jobs)
        - Indeed (50 jobs)
        - FlexJobs (30 jobs)
        - AngelList (25 jobs)
        
        Total: ~130 premium jobs
        """
        print("\n🔍 Scraping PREMIUM job sources...\n")
        
        all_jobs = []
        
        # Scrape each source with delays
        all_jobs.extend(self.scrape_linkedin_jobs(keywords, location, limit=25))
        time.sleep(3)  # Be polite
        
        all_jobs.extend(self.scrape_indeed(keywords, location, limit=50))
        time.sleep(3)
        
        all_jobs.extend(self.scrape_flexjobs(keywords, limit=30))
        time.sleep(2)
        
        all_jobs.extend(self.scrape_angellist(keywords, limit=25))
        
        print(f"\n✅ Total premium jobs collected: {len(all_jobs)}\n")
        return all_jobs

# ==========================================
# INTEGRATION WITH YOUR EXISTING SCRAPER
# ==========================================

class EnhancedJobScraper:
    """Enhanced scraper combining free and premium sources."""
    
    def __init__(self):
        self.basic_scraper = JobScraper()  # Your existing scraper
        self.premium_scraper = PremiumJobSources()
        self.jobs = []
    
    def scrape_all_sources(
        self, 
        keywords: List[str],
        include_premium: bool = True,
        include_basic: bool = True
    ) -> List[Dict]:
        """
        Scrape all available sources.
        
        Args:
            keywords: Job search keywords
            include_premium: Include LinkedIn, Indeed, etc.
            include_basic: Include RemoteOK, Remotive, etc.
        """
        all_jobs = []
        keyword_str = ' '.join(keywords)
        
        # Basic sources (fast, reliable)
        if include_basic:
            print("="*70)
            print("📦 SCRAPING BASIC SOURCES (Fast & Reliable)")
            print("="*70)
            basic_jobs = self.basic_scraper.scrape_all(keywords)
            all_jobs.extend(basic_jobs)
            time.sleep(2)
        
        # Premium sources (higher quality, slower)
        if include_premium:
            print("\n" + "="*70)
            print("💎 SCRAPING PREMIUM SOURCES (High Quality)")
            print("="*70)
            premium_jobs = self.premium_scraper.scrape_all_premium(keyword_str)
            all_jobs.extend(premium_jobs)
        
        # Remove duplicates by URL
        seen_urls = set()
        unique_jobs = []
        for job in all_jobs:
            if job['url'] and job['url'] not in seen_urls:
                seen_urls.add(job['url'])
                unique_jobs.append(job)
        
        print("\n" + "="*70)
        print(f"✅ TOTAL UNIQUE JOBS: {len(unique_jobs)}")
        print("="*70 + "\n")
        
        self.jobs = unique_jobs
        return unique_jobs

# Usage in your main code:
# Replace your JobScraper with EnhancedJobScraper
#
# scraper = EnhancedJobScraper()
# jobs = scraper.scrape_all_sources(
#     keywords=['data scientist', 'ai engineer'],
#     include_premium=True,  # Set to False if rate-limited
#     include_basic=True
# )
