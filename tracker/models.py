from django.db import models
from django.utils.timezone import now

class Thesis(models.Model):
    name = models.CharField(max_length=200)
    upload_date = models.DateTimeField(default=now)
    word_change = models.IntegerField()
    
    def __str__(self):
        return (f"{self.name} changed {self.word_change} words at {self.date}")