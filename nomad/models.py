from django.db import models
from django.conf import settings
# Create your models here.
class Feedback(models.Model):
    author              = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content             = models.TextField(blank=True, null=True)
    feedback            = models.CharField(verbose_name="feedback", null=True, blank=True, max_length=1000)
    timestamp           = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content[:20]

class Question(models.Model):
    author              = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    question            = models.TextField()
    answer              = models.TextField()
    is_answered         = models.BooleanField(default=False)
    timestamp           = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question[:20]

