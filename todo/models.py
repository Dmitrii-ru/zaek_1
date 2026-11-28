from django.db import models

from django.contrib.auth.models import User

# Create your models here.
class TodoTask(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    date = models.DateField()  # дата, к которой привязана задача
    text = models.CharField(max_length=255)
    is_closed = models.BooleanField(default=False) # False = actual, True = close
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['date', 'created_at']

    def __str__(self):
        return f"{self.date} - {self.text} ({'Done' if self.is_closed else 'Todo'})"