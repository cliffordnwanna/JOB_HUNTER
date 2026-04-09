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
            response = requests.get("https://remoteok.com/api", timeout=10, headers=self.headers)
            response.raise_for_status()
            data = response.json()
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
            response = requests.get("https://remotive.com/api/remote-jobs", timeout=10, headers=self.headers)
            response.raise_for_status()
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
            response = requests.get("https://jobicy.com/api/v2/remote-jobs?count=50", timeout=10, headers=self.headers)
            response.raise_for_status()
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
            response = requests.get("https://www.arbeitnow.com/api/job-board-api", timeout=10, headers=self.headers)
            response.raise_for_status()
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
            response = requests.get("https://himalayas.app/jobs/api?limit=50", timeout=10, headers=self.headers)
            response.raise_for_status()
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
            response = requests.get("https://weworkremotely.com/remote-jobs", timeout=10, headers=self.headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
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

    def scrape_all(self, keywords: List[str] = None, limit: int = 50, progress_callback=None, timeout: int = 10):
        """
        Scrape jobs from all sources in parallel with timeout per source.
        
        Args:
            keywords: Filter keywords
            limit: Max jobs per source
            progress_callback: Function(pct, message) for progress updates
            timeout: Max seconds per source (default 10s)
        """
        import concurrent.futures
        
        scrapers = [
            (self.scrape_remoteok, "RemoteOK"),
            (self.scrape_remotive, "Remotive"),
            (self.scrape_jobicy, "Jobicy"),
            (self.scrape_arbeitnow, "Arbeitnow"),
            (self.scrape_himalayas, "Himalayas"),
            (self.scrape_weworkremotely, "WeWorkRemotely")
        ]

        all_jobs = []
        total_scrapers = len(scrapers)
        completed = 0
        
        # Use ThreadPoolExecutor for parallel scraping with timeout
        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
            # Submit all scraping tasks
            future_to_scraper = {
                executor.submit(scraper_func, limit): name 
                for scraper_func, name in scrapers
            }
            
            # Collect results as they complete (with timeout)
            for future in concurrent.futures.as_completed(future_to_scraper):
                name = future_to_scraper[future]
                completed += 1
                
                try:
                    jobs = future.result(timeout=timeout)
                    all_jobs.extend(jobs)
                except concurrent.futures.TimeoutError:
                    print(f"⏱️ Timeout: {name} took longer than {timeout}s, skipping")
                except Exception as e:
                    print(f"❌ Error scraping {name}: {e}")
                
                if progress_callback:
                    progress_callback(completed / total_scrapers, f"🔍 Searched {name}...")

        # Filter by keyword
        if keywords:
            keywords_lower = [k.lower() for k in keywords]
            filtered = []
            for job in all_jobs:
                combined = (job.get('title', '') + ' ' + job.get('description', '')).lower()
                if any(kw in combined for kw in keywords_lower):
                    filtered.append(job)
            all_jobs = filtered

        # Remove duplicates (by URL and fuzzy title+company match)
        seen_urls = set()
        seen_signatures = set()
        unique_jobs = []
        
        for job in all_jobs:
            url = job.get('url', '')
            title = job.get('title', '').lower().strip()
            company = job.get('company', '').lower().strip()
            
            # Skip if exact URL already seen
            if url and url in seen_urls:
                continue
            
            # Create fuzzy signature (first 20 chars of title + company)
            # This catches same job with slightly different titles
            signature = f"{title[:20]}|{company[:15]}"
            if signature in seen_signatures:
                continue
            
            if url:
                seen_urls.add(url)
            seen_signatures.add(signature)
            unique_jobs.append(job)

        self.jobs = unique_jobs
        return unique_jobs
