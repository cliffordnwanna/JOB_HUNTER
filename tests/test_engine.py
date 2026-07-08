import unittest
from src.llm_extractor import HybridExtractor
from src.matcher_v2 import JobMatcher


class TestJobHunterEngine(unittest.TestCase):
    def setUp(self):
        self.extractor = HybridExtractor()
        self.mock_cv_text = "Experienced Python Developer with expertise in Azure, Machine Learning, and SQL."
        self.mock_cv_data = {
            "skills": ["Python", "Azure", "Machine Learning", "SQL"],
            "soft_skills": [],
            "full_text": self.mock_cv_text,
            "years_experience": 5,
        }

    def test_local_fallback_skill_extraction(self):
        """The regex fallback should extract known skill keywords without calling any LLM."""
        result = self.extractor._local_fallback(self.mock_cv_text)
        skill_names = [s.name.lower() for s in result.domain_knowledge]
        self.assertIn("python", skill_names)
        self.assertIn("azure", skill_names)

    def test_tfidf_matcher(self):
        """The matcher should produce a bounded score for a relevant job."""
        matcher = JobMatcher(self.mock_cv_data, match_mode="tfidf")
        job = {
            "title": "Azure AI Engineer",
            "description": "We are looking for a Python developer with Azure and machine learning experience.",
            "tags": [],
        }
        score = matcher.tfidf_matcher.match(self.mock_cv_data, job)
        self.assertGreater(score, 0)
        self.assertLessEqual(score, 100)

    def test_matcher_sorting(self):
        """Jobs should be ranked with the more relevant posting first."""
        matcher = JobMatcher(self.mock_cv_data, match_mode="tfidf")
        jobs = [
            {"title": "Chef", "description": "Cooking food in a kitchen", "tags": []},
            {"title": "Azure AI Developer", "description": "Building AI on Azure with Python and machine learning", "tags": []},
        ]
        scored_jobs = matcher.score_jobs(jobs)
        self.assertEqual(scored_jobs[0]["title"], "Azure AI Developer")


if __name__ == "__main__":
    unittest.main()
