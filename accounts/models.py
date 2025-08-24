from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid


# Create your models here.
class Student(AbstractUser):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    bio = models.TextField()
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    public_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def __str__(self):
        return  self.username




