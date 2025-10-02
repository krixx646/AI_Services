from django.test import TestCase
from rest_framework.test import APIClient


class SearchApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_search_requires_q(self):
        r = self.client.get("/api/search/")
        self.assertEqual(r.status_code, 400)

    def test_search_all_scopes(self):
        r = self.client.get("/api/search/?q=test&type=all")
        self.assertEqual(r.status_code, 200)
        self.assertIn("results", r.data)

