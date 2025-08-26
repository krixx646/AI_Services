from django.db import models
from django.conf import settings
from payments.models import BotInstance


class NoteAsset(models.Model):
    id = models.BigAutoField(primary_key=True)
    bot = models.ForeignKey(BotInstance, on_delete=models.CASCADE, related_name="note_assets")
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    file = models.FileField(upload_to="notes/")
    original_filename = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.original_filename or self.file.name

# Create your models here.
