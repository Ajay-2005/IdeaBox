from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now,timedelta
from django.conf import settings
import hashlib
import random
from django.core.validators import RegexValidator


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
	phone_number = models.CharField(
		max_length=15,
		blank=True,
		null=True,
		validators=[
			RegexValidator(
				regex=r'^[6-9]\d{9}$',  # Only accepts 10-digit numbers starting with 6, 7, 8, or 9
				message="Enter a valid 10-digit phone number starting with 6, 7, 8, or 9."
			)
		]
	)
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
	


class idea(models.Model):
	CATEGORY_CHOICES = [
		('Tech', 'Tech'),
		('Finance', 'Finance'),
		('Health', 'Health'),
		('Entertainment', 'Entertainment'),
		('Food', 'Food'),
	]
	VISIBILITY_CHOICES = [
		('Public', 'Public'),
		('Private', 'Private'),
	]

	title = models.CharField(max_length=150)
	description = models.TextField()
	category = models.CharField(
		max_length=100,
		choices=CATEGORY_CHOICES,
		default='Tech'
	)
	creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ideas')
	visibility = models.CharField(
		max_length=50,
		choices=VISIBILITY_CHOICES,
		default='Public'
	)
	target_audience = models.TextField(blank=True, null=True)  # Allows null/empty values
	market_opportunity = models.TextField(blank=True, null=True)  # Allows null/empty values
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.title

class Feedback(models.Model):
	idea=models.ForeignKey(idea,related_name='feedbacks',on_delete=models.CASCADE),
	mentor=models.ForeignKey(User,related_name='mentor_feedbacks',on_delete=models.CASCADE),
	content=models.TextField(),
	created_at=models.DateTimeField(auto_now_add=True),
	acknowledged=models.BooleanField(default=False)

	def __str__(self):
		return f" Feedback on {self.idea.title} by {self.mentor.username}"
	
class Tag(models.Model):
	name = models.CharField(max_length=50, unique=True)

	def __str__(self):
		return self.name

class Post(models.Model):
	title = models.CharField(max_length=255)
	description = models.TextField()
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	created_by = models.ForeignKey(User, on_delete=models.CASCADE)
	tags = models.ManyToManyField(Tag, related_name="questions")

	def __str__(self):
		return self.title

class Comment(models.Model):
    question = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="answers",default=1)
    content = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_comments",default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    upvotes = models.IntegerField(default=0)
    downvotes = models.IntegerField(default=0)

    def __str__(self):
        return f"Answer by {self.created_by.username}"


class Reply(models.Model):
    comment = models.ForeignKey(Comment, related_name='replies', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Reply by {self.user.username} on Comment {self.comment.id}"

class Vote(models.Model):
	UPVOTE = 1
	DOWNVOTE = -1
	VOTE_CHOICES = [(UPVOTE, "Upvote"), (DOWNVOTE, "Downvote")]
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	question = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True)
	answer = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, blank=True)
	value = models.IntegerField(choices=VOTE_CHOICES)

	class Meta:
		unique_together = ('user', 'question', 'answer')  


