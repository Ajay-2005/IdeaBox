from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now, timedelta
from django.conf import settings
import hashlib
import random

class User(AbstractUser):
    ROLE_CHOICES = [
        ('entrepreneur', 'Entrepreneur'),
        ('collaborator', 'Collaborator'),
        ('mentor', 'Mentor'),
    ]
    email = models.EmailField(unique=True)  
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='entrepreneur')
    otp_hash = models.CharField(max_length=64, blank=True, null=True)
    otp_created_at = models.DateTimeField(blank=True, null=True)

    def generate_otp(self):
        otp = str(random.randint(100000, 999999))  
        self.otp_hash = hashlib.sha256(otp.encode()).hexdigest()
        self.otp_created_at = now()
        self.save()
        return otp

    def verify_otp(self, otp):
        otp_hash = hashlib.sha256(otp.encode()).hexdigest()
        if self.otp_hash == otp_hash and now() <= self.otp_created_at + timedelta(minutes=5):
            return True
        return False



class Skill(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Profile(models.Model):
    username = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True) 
    twitter = models.URLField(blank=True, null=True) 
    github = models.URLField(blank=True, null=True)   
    skills = models.ManyToManyField(Skill, blank=True)
    education = models.CharField(max_length=260, blank=True, null=True)
    experience = models.TextField(blank=True, null=True) 
    bio = models.TextField(blank=True, null=True) 
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    status = models.CharField(max_length=100, choices=[('Available', 'Available'), ('Not Available', 'Not Available')], default='Available')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.username}"

