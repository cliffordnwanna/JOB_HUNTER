import requests
from bs4 import BeautifulSoup
from typing import List, Dict
import streamlit as st

class JobScraper:
    """Job scraper using multiple sources."""

    def __init__(self):
        self.jobs = []
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

    def scrape_remoteok(self, limit=50):
        """Scrape RemoteOK - one of the largest remote job boards."""
        try:
            data = requests.get("https://remoteok.com/api", timeout=15, headers=self.headers).json()
            jobs = []
            for item in data[1:limit+1]:
                if isinstance(item, dict):
                    jobs.append({
                        'title': item.get('position', ''),
                        'company': item.get('company', ''),
                        'location': 'Remote',
                        'description': item.get('description', ''),
                        'tags': item.get('tags', []),
                        'url': f"https://remoteok.com/remote-jobs/{item.get('id', '')}",
                        'salary': item.get('salary_min', 'Not specified'),
                        'posted_date': item.get('date', 'N/A'),
                        'source': 'RemoteOK'
                    })
            return jobs
        except Exception:
            return []

    def scrape_remotive(self, limit=50):
        """Scrape Remotive - curated remote jobs in tech."""
        try:
            response = requests.get("https://remotive.com/api/remote-jobs", timeout=15, headers=self.headers)
            data = response.json()
            jobs = []
            for item in data.get('jobs', [])[:limit]:
                jobs.append({
                    'title': item.get('title', ''),
                    'company': item.get('company_name', ''),
                    'location': item.get('candidate_required_location', 'Remote') or 'Remote',
                    'description': item.get('description', ''),
                    'tags': [item.get('category', '')],
                    'url': item.get('url', ''),
                    'salary': item.get('salary', 'Not specified') or 'Not specified',
                    'posted_date': item.get('publication_date', 'N/A'),
                    'source': 'Remotive'
                })
            return jobs
        except Exception:
            return []

    def scrape_jobicy(self, limit=50):
        """Scrape Jobicy - remote jobs worldwide."""
        try:
            response = requests.get("https://jobicy.com/api/v2/remote-jobs?count=50", timeout=15, headers=self.headers)
            data = response.json()
            jobs = []
            for item in data.get('jobs', [])[:limit]:
                jobs.append({
                    'title': item.get('jobTitle', ''),
                    'company': item.get('companyName', ''),
                    'location': item.get('jobGeo', 'Remote') or 'Remote',
                    'description': item.get('jobDescription', ''),
                    'tags': [item.get('jobIndustry', '')],
                    'url': item.get('url', ''),
                    'salary': f"{item.get('annualSalaryMin', '')} - {item.get('annualSalaryMax', '')}".strip(' -') or 'Not specified',
                    'posted_date': item.get('pubDate', 'N/A'),
                    'source': 'Jobicy'
                })
            return jobs
        except Exception:
            return []

    def scrape_arbeitnow(self, limit=50):
        """Scrape Arbeitnow - EU remote jobs."""
        try:
            response = requests.get("https://www.arbeitnow.com/api/job-board-api", timeout=15, headers=self.headers)
            data = response.json()
            jobs = []
            for item in data.get('data', []):
                if item.get('remote', False):
                    jobs.append({
                        'title': item.get('title', ''),
                        'company': item.get('company_name', ''),
                        'location': item.get('location', 'Remote') or 'Remote',
                        'description': item.get('description', ''),
                        'tags': item.get('tags', []),
                        'url': item.get('url', ''),
                        'salary': 'Not specified',
                        'posted_date': item.get('created_at', 'N/A'),
                        'source': 'Arbeitnow'
                    })
                    if len(jobs) >= limit:
                        break
            return jobs
        except Exception:
            return []

    def scrape_himalayas(self, limit=50):
        """Scrape Himalayas - remote-first company jobs."""
        try:
            response = requests.get("https://himalayas.app/jobs/api?limit=50", timeout=15, headers=self.headers)
            data = response.json()
            jobs = []
            for item in data.get('jobs', [])[:limit]:
                salary = 'Not specified'
                if item.get('minSalary'):
                    currency = item.get('salaryCurrency', '')
                    salary = f"{currency} {item.get('minSalary', '')}"
                jobs.append({
                    'title': item.get('title', ''),
                    'company': item.get('companyName', ''),
                    'location': 'Remote',
                    'description': item.get('description', ''),
                    'tags': item.get('categories', []) if isinstance(item.get('categories'), list) else [],
                    'url': f"https://himalayas.app/jobs/{item.get('slug', '')}",
                    'salary': salary,
                    'posted_date': item.get('pubDate', 'N/A'),
                    'source': 'Himalayas'
                })
            return jobs
        except Exception:
            return []

    def scrape_weworkremotely(self, limit=50):
        try:
            soup = BeautifulSoup(
                requests.get("https://weworkremotely.com/remote-jobs", timeout=15, headers=self.headers).text,
                "html.parser"
            )
            jobs = []
            for li in soup.select("li.feature")[:limit]:
                a = li.find("a", href=True)
                if not a:
                    continue
                jobs.append({
                    'title': li.select_one(".title").text.strip() if li.select_one(".title") else '',
                    'company': li.select_one(".company").text.strip() if li.select_one(".company") else '',
                    'location': 'Remote',
                    'description': '',
                    'tags': [],
                    'url': "https://weworkremotely.com" + a["href"],
                    'salary': 'Not specified',
                    'posted_date': 'Recent',
                    'source': 'WeWorkRemotely'
                })
            return jobs
        except Exception:
            return []

    def scrape_all(self, keywords: List[str] = None, limit: int = 50, progress_callback=None):
        """Scrape jobs from sources with specific limit."""
        all_jobs = []
        
        scrapers = [
            (self.scrape_remoteok, "RemoteOK"),
            (self.scrape_remotive, "Remotive"),
            (self.scrape_jobicy, "Jobicy"),
            (self.scrape_arbeitnow, "Arbeitnow"),
            (self.scrape_himalayas, "Himalayas"),
            (self.scrape_weworkremotely, "WeWorkRemotely")
        ]

        total_scrapers = len(scrapers)
        for i, (scraper_func, name) in enumerate(scrapers):
            if progress_callback:
                progress_callback((i + 1) / total_scrapers, f"🔍 Searching {name}...")
            all_jobs.extend(scraper_func(limit=limit))

        # Filter by keyword
        if keywords:
            keywords_lower = [k.lower() for k in keywords]
            filtered = []
            for job in all_jobs:
                combined = (job.get('title', '') + ' ' + job.get('description', '')).lower()
                if any(kw in combined for kw in keywords_lower):
                    filtered.append(job)
            all_jobs = filtered

        # Remove duplicates
        seen_urls = set()
        unique_jobs = []
        for job in all_jobs:
            url = job.get('url', '')
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_jobs.append(job)

        self.jobs = unique_jobs
        return unique_jobs
