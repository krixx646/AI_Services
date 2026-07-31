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

    def test_app_ads_txt_is_plain_text_at_root(self):
        response = self.client.get("/app-ads.txt")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/plain")
        self.assertEqual(
            response.content.decode(),
            "google.com, pub-3679558664849483, DIRECT, f08c47fec0942fa0\n",
        )

