from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.conf import settings


class User(AbstractUser):
    jwt_token = models.CharField(max_length=255, blank=True, null=True)
    webhook_url = models.URLField(blank=True, null=True)

    class Meta:
        swappable = 'AUTH_USER_MODEL'


class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    city = models.TextField()
    period_choices = [
        ('1', '1 hour'),
        ('3', '3 hours'),
        ('6', '6 hours'),
        ('12', '12 hours'),
    ]
    period = models.CharField(max_length=2, choices=period_choices)
    method_choices = [
        ('email', 'Email'),
        ('push', 'Push Notification'),
        ('webhook', 'Webhook'),
    ]
    method = models.CharField(max_length=10, choices=method_choices)
    last_notification_time = models.DateTimeField(null=True, blank=True)


class City(models.Model):
    name = models.CharField(max_length=255)


class WeatherData(models.Model):
    city = models.ForeignKey('City', on_delete=models.CASCADE)
    temperature = models.FloatField()
    humidity = models.FloatField(null=True)
    timestamp = models.DateTimeField(auto_now_add=True)


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    city = models.ForeignKey('City', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.content}"


class DefaultCity(models.Model):
    name = models.CharField(max_length=255)