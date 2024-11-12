from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('entrepreneur', 'Entrepreneur'),
        ('collaborator', 'Collaborator'),
        ('mentor', 'Mentor')
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='entrepreneur')

    def __str__(self):
        return f"{self.username}"


class Profile(models.Model):
    username=models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    skills=models.CharField(max_length=260,blank=True,null=True)
    education=models.CharField(max_length=260,blank=True,null=True)
    experience=models.CharField(max_length=260,blank=True,null=True)
    bio=models.CharField(blank=True,null=True)


    def __str__(self):
        return f"{self.username}"
    

