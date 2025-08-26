from django.db import models
from django.conf import settings
from payments.models import BotInstance


class Question(models.Model):
    id = models.BigAutoField(primary_key=True)
    bot = models.ForeignKey(BotInstance, on_delete=models.CASCADE, related_name="questions")
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=["bot", "created_at"])]

    def __str__(self) -> str:
        return self.text[:80]


class Answer(models.Model):
    id = models.BigAutoField(primary_key=True)
    question = models.OneToOneField(Question, on_delete=models.CASCADE, related_name="answer")
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Answer to: {self.question_id}"


class Review(models.Model):
    id = models.BigAutoField(primary_key=True)
    bot = models.ForeignKey(BotInstance, on_delete=models.CASCADE, related_name="reviews")
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=["bot", "created_at"])]

    def __str__(self) -> str:
        return f"{self.bot_id} - {self.rating}"

# Create your models here.
