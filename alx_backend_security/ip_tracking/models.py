from django.db import models
from django.utils import timezone

class RequestLog(models.Model):
    ip_address = models.CharField(max_length=45)
    timestamp = models.DateTimeField(default=timezone.now)
    path = models.CharField(max_length=200)
    country = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"{self.ip_address} - {self.path} - {self.timestamp}"
    
class BlockedIP(models.Model):
    ip_address = models.CharField(max_length=45, unique=True)

    def __str__(self):
        return self.ip_address
    
class SuspiciousIP(models.Model):
    ip_address = models.CharField(max_length=45, unique=True)
    reason = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.ip_address} - {self.reason} - {self.timestamp}"