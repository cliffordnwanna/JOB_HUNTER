import unittest
from src.parser import EnhancedCVParser
from src.matcher import JobMatcher

class TestJobHunterEngine(unittest.TestCase):
    def setUp(self):
        self.parser = EnhancedCVParser()
        self.mock_cv_text = "Experienced Python Developer with expertise in Azure AI, Machine Learning, and SQL."
        self.mock_cv_data = {
            "skills": ["Python", "Azure AI", "Machine Learning", "SQL"],
            "full_text": self.mock_cv_text,
            "years_experience": 5
        }

    def test_cv_skill_extraction(self):
        """Test if the parser correctly extracts skills from text."""
        skills = self.parser.extract_comprehensive_skills(self.mock_cv_text)
        self.assertIn("python", [s.lower() for s in skills])
        self.assertIn("azure ai", [s.lower() for s in skills])

    def test_tfidf_matcher(self):
        """Test if the matcher produces a score for relevant jobs."""
        matcher = JobMatcher(self.mock_cv_data)
        job = {
            "title": "Azure AI Engineer",
            "description": "We are looking for a Python developer with Azure AI experience."
        }
        score = matcher.tfidf_matcher.match(self.mock_cv_data, job)
        self.assertGreater(score, 0)
        self.assertLessEqual(score, 100)

    def test_matcher_sorting(self):
        """Test if jobs are correctly sorted by score."""
        matcher = JobMatcher(self.mock_cv_data)
        jobs = [
            {"title": "Chef", "description": "Cooking food in a kitchen"},
            {"title": "Azure AI Developer", "description": "Building AI on Azure with Python"}
        ]
        scored_jobs = matcher.score_jobs(jobs)
        self.assertEqual(scored_jobs[0]["title"], "Azure AI Developer")

if __name__ == "__main__":
    unittest.main()
