from django.db import models
from django.conf import settings
from django.utils import timezone

class Facility(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Booking(models.Model):
    PURPOSE_CHOICES = [
        ('booking', 'Booking'),
        ('block', 'Blocked by Staff'),
    ]
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    start_datetime = models.DateTimeField(default=timezone.now)
    end_datetime = models.DateTimeField(default=timezone.now)
    purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES, default='booking')
    reason = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
