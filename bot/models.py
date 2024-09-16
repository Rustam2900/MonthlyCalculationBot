from django.db import models


class User(models.Model):
    telegram_id = models.BigIntegerField(unique=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    username = models.CharField(max_length=100, unique=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name or 'No Name'}"


class MandatoryUser(models.Model):
    chat_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mandatory', null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    url = models.URLField(max_length=200)

    def __str__(self):
        return f"{self.name}"
