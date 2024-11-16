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



class Profile(models.Model):
    username=models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    skills=models.CharField(max_length=260,blank=True,null=True)
    education=models.CharField(max_length=260,blank=True,null=True)
    experience=models.CharField(max_length=260,blank=True,null=True)
    bio=models.CharField(blank=True,null=True)


    def __str__(self):
        return f"{self.username}"
    

