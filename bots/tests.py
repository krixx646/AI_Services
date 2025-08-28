from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from payments.models import BotInstance
from .models import Question, Answer


class BotsApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        User = get_user_model()
        self.user = User.objects.create_user(username="u2", email="u2@example.com", password="pass12345")
        self.bot = BotInstance.objects.create(owner=self.user, status=BotInstance.Status.READY)
        q = Question.objects.create(bot=self.bot, text="Hello?")
        Answer.objects.create(question=q, text="Hi!")

    def test_questions_and_answer(self):
        r = self.client.get(f"/api/bots/{self.bot.reference}/questions/")
        self.assertEqual(r.status_code, 200)
        self.assertGreaterEqual(len(r.data), 1)

        qid = r.data[0]["id"]
        r2 = self.client.post(f"/api/bots/{self.bot.reference}/answer/", {"question_id": qid}, format="json")
        self.assertEqual(r2.status_code, 200)
        self.assertIn("answer", r2.data)

# Create your tests here.
