# models.py
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import random
import secrets
from django.utils import timezone

class EmailVerification(models.Model):
    email = models.EmailField(unique=True)
    code = models.CharField(max_length=6)
    expires_at = models.DateTimeField()

    def is_valid(self):
        return timezone.now() <= self.expires_at

class Score(models.Model):
    total = models.IntegerField(default=0)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('analyst', 'Analyst'),
        ('normal_user', 'Normal User'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="normal_user")
    strike_count = models.PositiveIntegerField(default=0)
    is_banned = models.BooleanField(default=False)
    ban_expiry = models.DateTimeField(null=True, blank=True)

class BannedEmail(models.Model):
    email = models.EmailField(unique=True)
    banned_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email
    
    def check_ban_status(self):
        if self.is_banned and self.ban_expiry and timezone.now() > self.ban_expiry:
            self.is_banned = False
            self.ban_expiry = None
            self.save()