from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now

class Thesis(models.Model):
    username = models.CharField(max_length=200)
    upload_date = models.DateTimeField(default=now)
    total_words = models.IntegerField(default=0)
    word_change = models.IntegerField(default=0)
    
    def __str__(self):
        return (f"{self.username} changed {self.word_change} words at {self.upload_date}")
    
class CustomUser(AbstractUser):
    university = models.CharField(max_length=100, null=True, blank=True)