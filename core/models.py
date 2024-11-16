from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    body = models.TextField()
    file = models.FileField(upload_to='posts/', null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)