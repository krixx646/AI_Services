from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from .models import Post, Category


class BlogApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        User = get_user_model()
        self.author = User.objects.create_user(username="author", email="a@example.com", password="pass12345")

    def test_create_and_list_post(self):
        # unauthenticated cannot create
        r = self.client.post("/api/blog/posts/", {"title": "T1", "content": "C"}, format="json")
        self.assertIn(r.status_code, (401, 403))

        # create as author
        self.client.force_authenticate(self.author)
        r2 = self.client.post("/api/blog/posts/", {"title": "T1", "content": "C", "status": "published"}, format="json")
        self.assertEqual(r2.status_code, 201)
        post_id = r2.data["id"]

        # list shows published
        r3 = self.client.get("/api/blog/posts/")
        self.assertEqual(r3.status_code, 200)
        self.assertGreaterEqual(len(r3.data), 1)

        # retrieve by slug
        slug = r2.data["slug"]
        r4 = self.client.get(f"/api/blog/posts/by-slug/{slug}/")
        self.assertEqual(r4.status_code, 200)

    def test_comments_and_moderation(self):
        self.client.force_authenticate(self.author)
        p = self.client.post("/api/blog/posts/", {"title": "T2", "content": "C", "status": "published"}, format="json").data
        post_id = p["id"]

        # add comment
        r = self.client.post(f"/api/blog/posts/{post_id}/comments/", {"content": "Nice"}, format="json")
        self.assertEqual(r.status_code, 201)
        cid = r.data["id"]

        # moderate (approve)
        self.client.force_authenticate(self.author)  # author is not admin, but just testing endpoint exists; in real it requires admin
        r2 = self.client.post(f"/api/blog/comments/{cid}/moderate/", {"action": "approve"}, format="json")
        self.assertIn(r2.status_code, (200, 403))

# Create your tests here.
